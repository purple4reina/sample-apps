# payload-capture — how it works (and why it's hard to debug)

> This file is the answer key. The [README](./README.md) deliberately says nothing
> about *how* this app fails — a first-time on-call engineer is meant to debug it
> with Datadog alone. This document explains the design, walks the debugging
> journey, reveals the root cause, and shows why **pattern matching over captured
> payloads** is the feature that cracks it.

## The scenario

You just got paged. It's your first on-call rotation.

> **[High Errors]** `rey-settlement-processor` error rate is 40% (was ~0%).

Nothing was deployed. No one is in a change window. The processor code hasn't
shipped in months. The queue isn't backed up in a way that explains it. Errors
are just… happening now, and they weren't an hour ago. Go.

## Architecture

```
EventBridge (rate: 1 min)
        │
        ▼
  rey-settlement-producer ──► SQS: rey-settlement-queue ──► rey-settlement-processor
        (Node 22)                    │  (batchSize: 1)            (Node 22)
                                     └► DLQ after 3 receives: rey-settlement-dlq
```

- **Producer** (`src/producer/`) simulates an upstream "ledger-core" service
  owned by another team. Every minute it emits a batch (default 60) of
  settlement messages. It has **no bug**.
- **Processor** (`src/processor/`) is *your* service. It consumes one message
  per invocation, decodes it, and settles it. It has **no bug either.** Its code
  is correct for the format it was written against.
- Both functions run the Datadog extension with **`captureLambdaPayload: true`**,
  so each invocation's request payload is on its `aws.lambda` span.

The failure is not in anyone's code. It's in the **data** — a subtle change in
the shape of the payload flowing between two teams.

## The payload

Each SQS message body is a settlement instruction:

```json
{
  "schemaVersion": "1",
  "messageId": "0f6b…-uuid",
  "emittedAt": "2026-07-20T15:04:05.000Z",
  "origin": "ledger-core",
  "settlement": {
    "ref": "US00042704851337W",
    "valueDate": "2026-07-20",
    "amountMinor": 149900,
    "currency": "USD"
  },
  "counterparty": { "id": "CP-7A31", "name": "Meridian Clearing" }
}
```

The interesting field is `settlement.ref`. It is a **positional, fixed-width
composite key** — the kind you find all over payments/legacy/mainframe systems:

```
 U S 0 0 0 4 2 7 0 4 8 5 1 3 3 7 W
 └region┘└─ledgerId─┘└─sequence──┘└scheme┘
   0-1       2-7          8-15      16      (character offsets)
```

| field    | offset | width | example    | meaning                          |
|----------|--------|-------|------------|----------------------------------|
| region   | 0      | 2     | `US`       | booking region                   |
| ledgerId | 2      | 6     | `000427`   | source ledger                    |
| sequence | 8      | 8     | `04851337` | monotonic counter                |
| scheme   | 16     | 1     | `W`        | settlement rail (A/W/C/S) — a **routing key** |

The processor decodes it with a declarative layout table
(`REF_LAYOUT` in `src/processor/settlement.js`) — it slices each field by its
fixed offset. Note: **it is not doing `event["scheme"]`.** The scheme is
*derived* by position from a composite string. That distinction is the whole
point (see [Why it's hard](#why-its-hard-to-root-cause)).

## What changes (the root cause)

The upstream team's `sequence` counter outgrew 8 digits. They widened the field
to **10 digits**. That's it. A two-character change to one high-cardinality
field, buried inside a larger payload. No key was renamed. No key was added. The
JSON is still valid. `settlement.ref` is still a string. Every other field is
untouched.

But `ref` is **positional**, and the processor reads fields by fixed offset.
Widening `sequence` by 2 shifts **everything after it**:

```
stable  (8-digit sequence, len 17):  US 000427 04851337   W
next   (10-digit sequence, len 19):  US 000427 0004851337 W
                                     ^^ ^^^^^^ ^^^^^^^^^^  ^
offsets the processor still reads:   region   sequence[8:16]  scheme[16]
```

Decoding the **next** ref `US0004270004851337W` with the *old* layout:

| field    | offset | reads      | result                                    |
|----------|--------|------------|-------------------------------------------|
| region   | `[0:2)`  | `US`       | ✅ still correct                          |
| ledgerId | `[2:8)`  | `000427`   | ✅ still correct                          |
| sequence | `[8:16)` | `00048513` | ❌ wrong — grabbed 8 of the 10 digits (but still numeric, so **no error**) |
| scheme   | `[16:1)` | `3`        | ❌ a **digit**, not `A/W/C/S`             |

The decoded `scheme` is now `"3"`. It isn't in the routing table, so:

```js
// src/processor/settlement.js
function route(decoded, ctx) {
  const handler = SCHEME_HANDLERS[decoded.scheme];   // SCHEME_HANDLERS["3"] === undefined
  if (!handler) {
    throw new SettlementError('unroutable settlement instruction');
  }
  ...
}
```

**A change to the width of `sequence` surfaces as an unroutable-scheme error two
fields away.** The stack trace points at routing. The routing table is fine. The
schemes upstream sent were fine. Nothing about the error mentions the reference,
its length, or the sequence counter. That is the trap.

Because the producer emits the new format for only a *fraction* of traffic
(`DRIFT_RATIO`, default 0.4 — a partial upstream rollout), the two formats
**coexist**: ~60% of messages still decode cleanly and succeed, ~40% fail. That
is your "40% error rate," and it's why both an old and a new pattern are present
in the captured payloads at the same time.

## Why it's hard to root-cause

This app is deliberately built so that **every existing Datadog root-cause
surface dead-ends.** Walk the journey a real on-call would take:

1. **Serverless view / the High Errors monitor** tells you the error *rate* rose
   on `rey-settlement-processor`. That's the symptom you already know. It does
   not tell you why.

2. **Error Tracking** groups every failure into a *single* issue:
   `SettlementError: unroutable settlement instruction`. Error Tracking
   fingerprints on `service + error.type + error.message + top stack frame` only
   — it never reads span tags or payloads. Every bad payload throws the same
   error type, the same constant message, from the same line in `route()`, so
   they all collapse into one bucket. Opening it shows a stack that points at
   routing. Dead end — and a *misleading* one.

3. **The flame graph / stack trace** is opaque by construction. It says a scheme
   couldn't be routed. It says nothing about `settlement.ref`, string lengths,
   or `sequence`. (The message is a fixed string with no payload-derived tokens,
   so even Error Tracking's message normalization has nothing to split on.)

4. **Deployment Tracking / Faulty Deployment Detection** finds nothing. It keys
   off a `version` (`DD_VERSION`) delta and Lambda code/config changes via
   CloudTrail. Nothing was deployed. The change was in *data*, produced by
   *another team's* service, and the toggle that flips it is an **SSM parameter
   read by the producer** — the processor's code, config, and version never
   change. There is no deploy to correlate against.

5. **Watchdog RCA** supports exactly four root-cause types: version changes,
   traffic increases, instance failures, and disk exhaustion. A payload-shape
   change is none of them.

6. **Watchdog error outliers / correlations** work only over **faceted** tags,
   and Datadog caps/ discourages high-cardinality facets. `settlement.ref` and
   `messageId` are unique per message — they'll never be facets, so nothing
   "correlates errors with tag X." The low-cardinality fields don't help either:
   errors span all regions and all schemes.

7. **Logs / Log Patterns** are no help. The processor logs one line:
   `settlement <messageId> rejected: unroutable settlement instruction`. Log
   Patterns masks the UUID and clusters it into a *single* pattern. No structure
   leaks.

8. **Faceting the captured payload** is the natural next move — and it fails too.
   The payload is captured (that's required for this feature), but
   `function.request.*` for an SQS trigger is the message envelope, and the body
   is a stringified JSON blob that is **unique on every span**. Faceting it gives
   you thousands of singletons. You can *see* a payload on any one failing trace,
   but with every value unique you have no way to know which part of it is
   *abnormal* without a notion of what "normal" looks like across the population.

Every existing tool keys off one of: error identity, an aggregate metric
deviation, a code/config **version** delta, or an overrepresented **faceted**
value. **None of them inspects the *structure* of a high-cardinality captured
payload.** That is the gap.

## The feature: pattern matching over captured payloads

Datadog already does exactly the right thing for **logs**: the Log Explorer
*Patterns* view clusters messages into templates, replacing the parts that vary
with `X`/`*` placeholders, so a human sees the *shape* of their data and can spot
the outlier cluster instantly.

Apply that same clustering to **captured payloads** and this incident solves
itself. Cluster the `function.request` payloads on the failing service and the
`settlement.ref` field resolves into two templates:

```
  LL999999########L    (17 chars)   ← ~all successes
  LL999999##########L  (19 chars)   ← 100% of the errors      ◄── there it is
```

Two clusters. One is two characters longer than the other, and it lines up
exactly with the errors. You don't need to know the format, read the parser, or
guess. The **shape** of the data tells you a field grew, and the correlation with
errors tells you it matters. From "40% of settlements are failing and the stack
says routing" to "a field in the upstream reference got two characters longer" —
in one view.

That is the pitch: *we love Log Patterns; here is the incident that proves we
need Payload Patterns.*

> Note on the captured tag path: with an SQS trigger the payload lands under
> `function.request.Records.0.body` as a JSON string (the tracer flattens JSON
> structure, but the SQS body is itself a string). Pattern-clustering that string
> is the closest analog to Log Patterns and works regardless of nesting. If a
> future tracer version parses the nested body, the same field appears as
> `function.request.Records.0.body.settlement.ref`. Worth validating empirically
> in the target org, per the Datadog docs (array/nested flattening is documented
> for the sibling AWS-SDK payload-tagging feature, not the Lambda one).

## The toggle

The upstream format is controlled by one SSM String parameter:

```
/rey/payload-capture/format-generation   (default: stable)
```

The producer reads it at runtime (`GetParameter`) and, when it's not `stable`,
emits `DRIFT_RATIO` of the batch in that generation. Flipping it is a data-only
change — **it never touches the processor**, which is what keeps deployment
tracking and faulty-deployment detection blind. `scripts/set-generation.sh`
writes the parameter; `npm run drift` → `next`, `npm run heal` → `stable`.

## Drift modes (a whole toolkit, not one trick)

The same fixed processor pipeline breaks in different, equally opaque ways
depending on the generation. Set any of these as the parameter value:

| generation     | what the upstream changed                                  | processor fails at            | opaque error                          |
|----------------|------------------------------------------------------------|-------------------------------|---------------------------------------|
| `stable`       | nothing                                                    | —                             | (healthy)                             |
| `next`         | `sequence` field widened 8 → 10 digits                     | `route()`                     | `unroutable settlement instruction`   |
| `scheme-case`  | routing key emitted lower-case (`W` → `w`), same length    | `route()`                     | `unroutable settlement instruction`   |
| `datetime`     | `valueDate` format `YYYY-MM-DD` → `MM/DD/YYYY`             | `resolveSettlementWindow()`   | `settlement outside permitted window` |
| `counterparty` | `counterparty.id` promoted from a string to a nested object| `resolveCounterparty()`       | `counterparty not recognized`         |

The killer demonstration is running **`next` and `scheme-case` together** (or one
then the other): they throw the *identical* error, from the *identical* line, so
Error Tracking shows **one issue** — but the captured payloads form **two
distinct patterns** (a 19-char reference cluster and a lower-case-scheme
cluster), i.e. **two different root causes hiding inside one error bucket.**
Payload patterns separate them; nothing else can.

`datetime` and `counterparty` show the feature generalizes beyond length: a
**format** change and a **type/shape** change, each caught as a distinct
structural cluster (`##/##/####` vs `####-##-##`; a scalar `id` vs a nested
object).

## Verifying the mechanism locally (no AWS)

```
$ node -e '
  const { buildMessage } = require("./src/producer/format");
  const { processSettlement } = require("./src/processor/settlement");
  for (const gen of ["stable","next","scheme-case","datetime","counterparty"]) {
    // force the drift for the demo (bypass the DRIFT_RATIO sampling)
    const m = buildMessage(gen);
    try { processSettlement(m); console.log(gen.padEnd(13), "OK  ", m.settlement.ref); }
    catch (e) { console.log(gen.padEnd(13), "FAIL", m.settlement.ref, "->", e.message); }
  }'
```

Expect `stable` to succeed and the other four to fail with the errors above.
(`buildMessage(gen)` always applies the drift; in the deployed producer only a
`DRIFT_RATIO` fraction does, which is what produces a *partial* error rate.)

## How you'd actually fix it

Once payload patterns reveal that `settlement.ref` grew, the fix is a
conversation and a small code change — pick per your change-management norms:

- **Short term:** coordinate with ledger-core to roll the format back
  (`npm run heal`) while you ship a parser fix.
- **Real fix:** stop decoding by absolute offset. Either read the reference
  right-to-left (scheme is always the last character; region the first two), or
  make the format self-describing (a delimiter, or a length/version prefix), or
  validate `ref.length` against the layout and reject/branch explicitly instead
  of silently mis-slicing.
- **Guardrail:** a payload-pattern monitor on the processor's captured payloads
  that alerts when a *new* structural cluster appears — catching the next format
  drift before it becomes a page.

## File map

```
apps/payload-capture/
├── bin/payload-capture.ts          CDK app entry (sa-east-1)
├── lib/payload-capture-stack.ts    SQS + DLQ + 2 Lambdas + schedule + SSM + DatadogLambda x2
├── src/
│   ├── producer/
│   │   ├── handler.js              reads the SSM generation, emits a batch to SQS
│   │   └── format.js               builds messages; applies each drift generation
│   └── processor/
│       ├── handler.js              SQS-triggered; throws on failure (→ retry → DLQ)
│       └── settlement.js           the fixed-width decode → window → counterparty → route pipeline
├── scripts/
│   ├── set-generation.sh           writes the SSM parameter (drift / heal)
│   └── invoke-producer.sh          one-shot producer invoke
├── cdk.json  tsconfig.json  package.json  .gitignore
├── README.md                       generic; no spoilers
└── CLAUDE.md                       this file
```
