# rey-settlement-processor Debugging Log

**Date:** 2026-07-20
**Scope constraint given by user:** investigate using Datadog only — no repo/code access.
**Trigger:** user observed `service:rey-settlement-processor` (Lambda) started failing recently.

This document walks through the investigation in the order it happened: every tool call, why I made it, what it returned, and which paths were dead ends vs. which ones led to the root cause.

---

## Step 1 — Load Datadog skill guidance

**Calls:**
- `mcp__plugin_datadog_mcp__list_datadog_skills` with query `"logs lambda serverless traces"`
- `mcp__plugin_datadog_mcp__search_datadog_logs` (in parallel) with query `service:rey-settlement-processor status:error`, `from=now-1d`, `use_log_patterns=true`, `pattern_group_by=["service"]`

**Why:** Before querying, I checked whether a domain-specific Datadog skill (logs/serverless/traces) existed to avoid query-syntax mistakes. In parallel I ran a first-pass log pattern search since the skill lookup doesn't depend on it.

**Result:** No single skill named exactly for "lambda/serverless" surfaced as a strong match (closest were generic ones like `datadog/querying-patterns`); I didn't load a skill and proceeded directly with tool descriptions. The log pattern search was immediately productive — see Step 2.

---

## Step 2 — First real signal: log pattern clustering

**Result of the parallel `search_datadog_logs` call above:**

Two dominant error patterns, both service=rey-settlement-processor:

1. `ERROR settlement * rejected: unroutable settlement instruction` — 2,503 occurrences
2. `ERROR Invoke Error {"errorType":"SettlementError","errorMessage":"unroutable settlement instruction", ... stack: at route (/var/task/settlement.js:93:11) at processSettlement (/var/task/settlement.js:104:10) at exports.handler (/var/task/handler.js:16:7) ...}` — 2,497 occurrences

**First seen:** `2026-07-20T20:17:16.384Z`
**Last seen (at query time):** `2026-07-20T20:56:16.910Z`

**Why this mattered:** This immediately told me:
- There is exactly one failure mode (`SettlementError: unroutable settlement instruction`), not a grab-bag of unrelated errors.
- It's thrown from application code (`settlement.js:93`, function `route()`), not an AWS/infra-level failure (no timeout, no throttle, no permission error).
- It has a sharp, precise onset time (20:17:16), which is a strong hint that *something changed* right around then rather than a gradual degradation.

This was the pivot point that shaped the rest of the investigation: find out why `route()` started rejecting instructions at 20:17:16, and for what subset of traffic.

---

## Step 3 — Pull raw log detail on the error

**Call:** `search_datadog_logs` with query `service:rey-settlement-processor status:error unroutable`, `extra_fields=["*"]`, `from=now-1d`

**Why:** The pattern view only showed a templated message; I needed to see actual attribute values (error object, stack, tags) to look for anything routing-relevant (e.g., a routing key, destination code) logged alongside the error.

**Result:** Confirmed the same stack trace repeatedly, plus infra tags (`runtime:nodejs22.x`, `dd_cdk_construct:v3.12.0`, CloudFormation stack `reypayloadcapturestack`, region `sa-east-1`, account `425362996713`). No routing key or instruction payload was present in the *log* attributes — the log line itself doesn't carry the settlement details, just the request ID and error. This told me I needed to go to **APM spans**, which capture the actual Lambda event payload (`function.request.Records[0].body`), to see what was actually being routed.

**Dead end (partial):** logs alone didn't have enough payload detail to find the differentiator between failing and succeeding messages — had to move to spans.

---

## Step 4 — Pull APM spans to see actual payload content

**Calls (parallel):**
- `search_datadog_spans` with query `service:rey-settlement-processor`, `custom_attributes=["*"]`, `from=now-1d`
- `search_datadog_logs` with query `service:rey-settlement-processor`, time window `2026-07-20T20:00:00Z`–`2026-07-20T20:20:00Z`, sorted ascending — trying to see what was happening in logs right before/at the 20:17:16 onset (deploy markers, config logs, version bumps, etc.)

**Why:** Spans on Lambda functions instrumented with `datadog-lambda-js` capture the full SQS record body (`function.request.Records.0.body`), which includes `counterparty`, `settlement.currency`, `settlement.amountMinor`, `settlement.ref`, `settlement.valueDate`, `origin`, `schemaVersion`. This was the first place I could see actual settlement instruction content. The parallel log query around the onset window was a check for an explicit "cause" event (e.g., a config/version log line) right at 20:17:16.

**Result:**
- Spans showed the SQS trigger is `arn:aws:sqs:sa-east-1:425362996713:rey-settlement-queue`, sender `rey-settlement-producer`, origin `ledger-core`. Failing and succeeding spans both had full payloads with `counterparty.id`, `settlement.currency`, `settlement.ref`, `settlement.amountMinor`, `settlement.valueDate`.
- The 20:00–20:20 log window was **a dead end** — it was just a wall of `START RequestId:.../END RequestId:...` Lambda lifecycle lines (invocation noise), no version/deploy/config markers visible in logs at all. This ruled out "check the raw logs for a marker" as a way to find the trigger event, and pushed the investigation toward statistical comparison of failing vs. succeeding payloads instead.

At this point I had a key qualitative observation from eyeballing a handful of spans: the **same counterparty** (`CP-7A31`, "Meridian Clearing") appeared in both a failing GBP span and a succeeding EUR span. That ruled out "this counterparty is just broken" as an explanation, and pointed toward the answer being in the settlement details themselves rather than the counterparty/currency combination.

---

## Step 5 — Test the counterparty/currency hypothesis (dead end)

**Calls (parallel):**
- `aggregate_spans`: `service:rey-settlement-processor status:error`, grouped by `currency` + `counterparty.id`
- `aggregate_spans`: `service:rey-settlement-processor status:ok`, grouped by `currency` + `counterparty.id`

**Why:** If routing were broken for a specific corridor (e.g., "GBP payments to CP-1F09 are unroutable because that route was deleted from a lookup table"), I'd expect some currency/counterparty combinations to be 100% error and others 100% success.

**Result — dead end:** All 20 combinations (5 counterparties × 4 currencies) had **both** errors and successes, in roughly the same proportion (errors ~115–171 per bucket, successes ~231–292 per bucket — a fairly uniform ~35–40% failure rate everywhere). This ruled out counterparty and currency as the differentiator. Routing-table-per-corridor theory rejected.

---

## Step 6 — Test the value-date hypothesis (dead end)

**Calls (parallel):**
- `aggregate_spans`: `status:error` grouped by `settlement.valueDate`
- `aggregate_spans`: `status:ok` grouped by `settlement.valueDate`
- `aggregate_spans`: `status:error` with `group_by.interval=300000` (5-minute time buckets, no field grouping) — to characterize the error rate over time

**Why:** Wondered if valueDate (e.g., a stale/past-dated instruction) triggered rejection, and separately wanted to see whether the error rate was a step function, a spike-then-decay, or ramping.

**Result:**
- Value-date distribution was essentially flat and matched between errors and successes (each date ~500–650 errors, ~980–1080 successes) — **dead end**, valueDate is not the cause.
- The 5-minute time-bucket histogram showed: 89 errors in the `20:15–20:20` bucket (i.e., right at/after the 20:17:16 onset), then a sustained plateau of ~360–420 errors per 5-minute bucket through `20:50–20:55`, tapering slightly in the last partial bucket. This confirmed the failure is a **persistent step change**, not a transient blip — consistent with an upstream change that's still in effect, not a one-off retry storm.

---

## Step 7 — Test the settlement reference (`ref`) format hypothesis

**Calls (parallel):**
- `aggregate_spans`: `status:error` grouped by `settlement.ref` (limit 30)
- `aggregate_spans`: `status:ok` grouped by `settlement.ref` (limit 30)

**Why:** Having ruled out counterparty, currency, and value-date, the remaining candidate fields in the payload were `ref` and `amountMinor`. I looked at the actual ref strings returned in both buckets.

**Result — this was the breakthrough:** Visually scanning the top-30 refs:
- **All** top error refs had the shape `<2-letter prefix><16 digits><1 trailing letter>`, e.g. `GB3629730088064350W`, `EU0045090030096442C`, `JP0671820023311312A` (19 characters total).
- **Almost all** top success refs had the shape `<2-letter prefix><14 digits><1 trailing letter>`, e.g. `GB46326832969925C`, `EU01548608616483S` (17 characters total) — one exception noted (`GB0340880035777649W`, 16-digit body, count 3, in the success bucket).

This was the first hypothesis where the two populations looked visibly, structurally different rather than just proportionally different.

---

## Step 8 — Try to confirm via schema version and regex query (partial dead end)

**Calls (parallel):**
- `aggregate_spans`: `status:error` grouped by `schemaVersion`
- `aggregate_spans`: `status:ok` grouped by `schemaVersion`
- `aggregate_spans`: attempted query with a regex-style filter directly in the query string: `status:error @function.request.Records.0.body.settlement.ref:/[A-Z]{2}[0-9]{16}[A-Z]/`

**Why:** Wanted a stronger, message-envelope-level signal (e.g., a `schemaVersion` bump) that would explain a ref-format change cleanly, and tried to get an exact count of "16-digit ref" errors via a regex filter instead of eyeballing samples.

**Result:**
- `schemaVersion` was `"1"` for **100%** of both errors (2,968) and successes (5,178) — **dead end**. The message envelope/schema version did *not* change; whatever changed did so silently within a field that's still nominally "schema v1".
- The regex-in-query attempt failed outright: `InvalidArgument: Cannot parse query` — **dead end**, this MCP tool's query syntax doesn't support inline regex on nested `@` attributes the way I tried it. Had to fall back to a different method (pulling raw samples and counting locally) instead of getting an exact aggregate count.

---

## Step 9 — Get a larger raw sample to confirm the ref-length pattern statistically

**Calls (parallel):**
- `search_datadog_spans`: `status:error`, `custom_attributes` restricted to `["function.request.Records.0.body.settlement.ref", "function.request.Records.0.body.settlement.amountMinor"]`, `max_tokens=15000`
- `search_datadog_spans`: same but `status:ok`

**Why:** Wanted a larger, cheaper sample (restricting to just two fields) to count the ref-length distribution more rigorously than the top-30 aggregate view, and to check whether `amountMinor` was a red herring or also correlated.

**Result:** Both calls **exceeded the tool's token limit** and were auto-saved to local files instead of being returned inline (each ~59KB / ~1,300+ lines). This was a mechanical detour, not a dead end in the analytical sense — it meant I had to pivot from "read the tool output directly" to "grep the saved files with Bash."

---

## Step 10 — Grep the saved sample files locally

**Calls (sequential, since the second depended on knowing the first worked):**
- `grep -oE 'ref: [A-Z]{2}[0-9]+[A-Z]' <error-sample-file> | awk '{print length($2)-3}' | sort | uniq -c`
- same for the `<ok-sample-file>`

**Why:** Rather than paying to re-read tens of thousands of characters into the model context, I used `grep`/`awk` locally to extract just the numeric-body length of each `ref` string and tally the distribution — a much cheaper way to test the hypothesis at scale.

**Result:**
```
ERROR sample: 9 refs, ALL with 16-digit numeric body
OK sample:    10 refs with 14-digit numeric body, 1 with 16-digit body
```
This confirmed the pattern from Step 7 was not a fluke of the top-30 sort order — it held in an independently drawn sample.

**Follow-up check (the one exception):** I grepped `-B5` around that single 16-digit `ok` ref (`US7929890030178656W`) to inspect its surrounding context and rule out a parsing mistake on my part (e.g., accidentally matching `amountMinor` instead of `ref`). It was a genuine `ref:` field, genuinely 16 digits, genuinely on a `status:ok` span. So the correlation is very strong (~95%) but not deterministic/absolute — consistent with the theory that occasional 16-digit refs slip through by coincidence (see "Solution" caveat below) rather than every 16-digit ref failing 100% of the time by hard rule.

**Dead-end sanity check:** I ran `wc -l` and re-grepped both saved files to make sure the small sample size (9 and 11 matches out of 1,343/1,405 lines) wasn't itself an artifact of a truncated/broken response. The files were legitimately mostly YAML indentation/boilerplate per span, not hidden additional ref matches — so 9 and 11 were the real number of distinct spans returned, not a parsing failure on my part.

---

## Step 11 — Look for an explicit deploy/change event to corroborate timing (dead end)

**Calls (parallel):**
- `get_change_stories` for `service_name: rey-settlement-producer`, window `2026-07-20T19:45:00Z`–`2026-07-20T20:30:00Z`
- `get_change_stories` for `service_name: rey-settlement-processor`, same window

**Why:** If a deploy/config/feature-flag change was tracked in Datadog for either the producer or processor around 20:17:16, that would directly confirm *what* changed and *who* changed it, rather than inferring it from payload shape alone.

**Result — dead end:** Both calls returned `{"stories":[],"truncated":false}` — no tracked change events for either service in that window. This likely means change tracking isn't wired up for these services in this account, not that nothing changed. I noted this limitation explicitly in the final write-up rather than treating the absence of change events as evidence against the hypothesis.

---

## Step 12 — Final aggregate sanity check on the fix confidence

**Call:** `Bash: wc -l` + `grep -c` on both saved sample files (already covered above in Step 10) — done as a final gut-check before writing up findings, to make sure the sample counts I was citing (9 vs. 11) were accurate and not a stale/cached read.

---

## Summary of dead ends (things that did NOT explain the failure)

| Hypothesis | How tested | Result |
|---|---|---|
| Counterparty-specific routing gap | `aggregate_spans` grouped by counterparty × currency, error vs. ok | Every combination had both errors and successes — rejected |
| Currency-specific routing gap | Same as above | Rejected |
| Stale/past `valueDate` | `aggregate_spans` grouped by valueDate, error vs. ok | Flat distribution, no correlation — rejected |
| Explicit deploy/config marker in raw logs at onset | `search_datadog_logs` over 20:00–20:20 window | Only Lambda lifecycle noise (START/END RequestId), no marker — rejected as a discovery method |
| Message schema version bump | `aggregate_spans` grouped by `schemaVersion` | 100% `"1"` on both sides — rejected |
| Regex filter directly in span query | `aggregate_spans` query with inline `/regex/` on nested attribute | Tool rejected the query syntax outright — method dead end, had to sample+grep instead |
| Tracked deployment/change event | `get_change_stories` for both producer and processor | No stories returned — inconclusive/unavailable, not usable as corroboration |

## What actually worked

1. Log pattern clustering (`use_log_patterns=true`) to identify the single dominant error signature and its stack trace fast.
2. Pivoting from logs → APM spans to get access to the actual SQS payload content (`function.request.Records.0.body`), since logs didn't carry settlement details.
3. Systematically eliminating dimensions (counterparty, currency, valueDate, schemaVersion) via `aggregate_spans` group-by before landing on `settlement.ref` format as the actual differentiator.
4. Falling back to local `grep`/`awk` over saved raw-sample files when the MCP tool's own aggregation/regex features couldn't answer the specific structural question ("what's the digit-length distribution of this string field") that Datadog's query language doesn't directly expose.

## Root cause (as reported to user)

Starting at **2026-07-20 20:17:16 UTC**, `rey-settlement-producer`/`ledger-core` began emitting `settlement.ref` values in a longer format (`<prefix><16 digits><letter>`, 19 chars) alongside/instead of the previous format (`<prefix><14 digits><letter>`, 17 chars). `rey-settlement-processor`'s `route()` function (`/var/task/settlement.js:93`) most likely extracts a routing/bank key via a fixed-offset slice of `ref` sized for the 14-digit format; the extra 2 digits shift that slice for ~35–40% of traffic, producing a lookup miss and the `SettlementError: unroutable settlement instruction` seen in both logs and APM error spans (Error Tracking issue `01dba466-8478-11f1-9ab5-da7ad0900002`).

## Proposed fix (as reported to user)

1. Make `route()` parse `ref` structurally (prefix + variable-length numeric body + check letter) instead of assuming a fixed total length.
2. Confirm with the `rey-settlement-producer`/`ledger-core` owners whether the longer reference format is an intentional migration; if so, add an explicit schema-version bump so consumers don't have to infer format changes from string length.
3. Short-term: route unroutable instructions to a DLQ/manual-review queue instead of dropping them, so no settlement instructions are lost while the fix ships.
