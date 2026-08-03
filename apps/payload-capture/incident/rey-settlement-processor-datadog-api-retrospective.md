# Retrospective: Datadog API Experience Debugging `rey-settlement-processor`

This is a reflective analysis of the original `rey-settlement-processor` incident investigation (conducted with Lambda payload capture **enabled**), focused specifically on the Datadog tooling/API experience — not the incident itself. Two questions are addressed:

1. What Datadog APIs or data availability would have gotten me to the solution faster and/or with more confidence?
2. How easy was it to query captured Lambda payloads, and what would I improve?

## Context: what actually happened

The root cause (a `settlement.ref` format change from 14 to 16 digits) was found by:
- Using log pattern clustering to isolate the error signature fast.
- Pulling raw span samples restricted to two `custom_attributes` (`function.request.Records.0.body.settlement.ref`, `function.request.Records.0.body.settlement.amountMinor`) via `search_datadog_spans`.
- Because the result set exceeded the tool's inline token budget, the results were auto-saved to local `.txt` files, and I fell back to Bash `grep`/`awk` to compute digit-length distributions across error vs. ok samples.
- A prior attempt to do this analytically inside Datadog — `aggregate_spans` with an inline regex on the nested attribute (`@function.request.Records.0.body.settlement.ref:/[A-Z]{2}[0-9]{16}[A-Z]/`) — failed outright with `InvalidArgument: Cannot parse query`.

That fallback-to-local-grep path worked, but it took more turns and more manual data-shape guessing than it should have for what is fundamentally a "compare the distribution of a field between two cohorts" question — a bread-and-butter aggregation query.

## Part 1 — What would have helped go faster / with more confidence

### 1. Regex / pattern matching over nested payload-capture attributes in `aggregate_spans`

The single biggest friction point. `search_datadog_spans` supports free-text/tag filtering reasonably well, but `aggregate_spans` — the tool that actually does grouping, percentiles, and counting — rejects any query with inline regex against a nested attribute path. This forced a manual "pull raw samples → export to file → grep locally" loop instead of a single API call like:

```
aggregate_spans(
  query: "service:rey-settlement-processor status:error",
  group_by: [{ field: "@function.request.Records.0.body.settlement.ref", regex: "^[A-Z]{2}[0-9]{16}" }],
  compute: [{ aggregation: "count" }]
)
```

If nested-attribute regex grouping/filtering were supported (even as a distinct, explicit parameter rather than inline query syntax, to avoid ambiguity with tag-query parsing), the entire "is the ref format different between error and ok cohorts" question would have been one call instead of four (two raw-sample pulls, two local greps) plus the false start on inline regex.

**Why this matters beyond this incident:** payload-capture data is exactly the kind of data where the interesting signal is a *shape* or *format* of a value (an ID pattern, a version prefix, an enum value from a new deploy), not a fixed literal you can equality-filter on. Nested-attribute regex support in aggregation is the difference between "detect a payload schema drift statistically in one query" and "eyeball a sample and hope it's representative."

### 2. Log-style pattern clustering, extended to captured payload field values

Datadog's log pattern clustering (used elsewhere in this incident — see the original writeup's log-analysis step) already solves almost exactly this problem for free-text log messages: it tokenizes message text, replaces variable substrings with placeholders, groups everything that reduces to the same template, and returns each cluster's template, count, first/last-seen timestamps, and sample lines. That's a fast, *proactive* way to see "the shape of the haystack" without hypothesizing what you're looking for first — which is exactly what was missing from the regex-aggregation idea above (#1 still requires me to guess "maybe it's a digit-count thing" before I can test it).

The natural extension: run the same clustering machinery over individual captured payload field *values*, not just log message text. Concretely, cluster `@function.request.Records.0.body.settlement.ref` (or any nested payload attribute) the same way log lines are clustered, and return cluster templates + counts + first/last-seen + samples — e.g. two clusters, `<ALPHA:2><DIGIT:14><ALPHA:1>` and `<ALPHA:2><DIGIT:16><ALPHA:1>`, with the second cluster's first-seen timestamp landing exactly at the error-onset time and its membership overlapping ~100% with `status:error` spans. That's the whole root cause, surfaced by one call, with no upfront hypothesis required.

**The design nuance that makes or breaks this:** standard log-pattern tokenization deliberately *collapses* variable-length runs — two different-length numeric IDs both become the same generic `<NUM>` placeholder, because for free-text logs, exact length is almost never the signal. In this incident, length *was* the signal (14 digits vs. 16). A naive reuse of log-clustering tokenization on payload values would merge both `ref` formats into one cluster and hide the exact anomaly that mattered. The useful variant needs length-aware, character-class-based signatures for structured field values specifically (bucket by character class *and* length range, rather than collapsing all digit runs to one wildcard) — distinct enough to preserve length-based drift, but not so literal that it degenerates into "list of distinct values." This is a real design tension specific to structured/semi-structured fields, and doesn't apply to the free-text case log clustering was originally built for.

If this had existed, the investigation would likely have collapsed from "restrict to two attributes → pull raw samples twice → export to file → grep/awk digit-length distributions by hand" down to a single clustering call that directly names both shapes, their onset times, and their correlation with error status — probably the fastest path to root cause of anything proposed in this document.

### 3. A dedicated schema/shape-diff endpoint for captured payload attributes

Related to #1 and #2 but more targeted at *confirming* a specific hypothesis once you have one (whereas #2 is about *discovering* the anomaly without a hypothesis): something like a `diff_span_attribute_shapes` call that takes two queries (e.g., "before timestamp X" vs "after timestamp X", or "status:error" vs "status:ok") and a nested attribute path, and returns a distribution summary — value length histogram, character-class histogram, cardinality, sample values — without me having to guess which attribute to pull, pull raw samples, and manually characterize them. Useful as a targeted follow-up once clustering (#2) has pointed at a specific field, or as a standalone tool when you already suspect a specific attribute and just want the two-cohort comparison directly.

### 4. Clearer, queryable indexing of *which* custom attributes exist on a service's spans

I had to guess the exact attribute path (`function.request.Records.0.body.settlement.ref`) somewhat blindly — I knew the general namespace (`function.request.*` from prior knowledge of the payload-capture feature) but not the exact nested path until a broad, unrestricted sample pull showed me the full JSON shape. A "list distinct attribute keys observed on this service in the last N hours" call (schema discovery, similar to what facet/tag-browsing already does for top-level tags) extended to reach into nested JSON payload attributes would have let me skip the initial broad/expensive sample pull entirely.

### 5. Silent-failure modes in `aggregate_spans` group_by are a confidence tax, not just a speed tax

Unrelated to payload capture specifically, but relevant to "more confidence": grouping by a bare attribute name (`cold_start`) instead of the `@`-prefixed nested form (`@cold_start`) doesn't error — it silently returns zero buckets. This is dangerous in exactly the way that matters for incident response: a silent empty result looks identical to "this hypothesis is false" (e.g., "cold starts aren't correlated with errors") when it's actually "the query was malformed." I caught it here because zero buckets was suspicious given known error volume, but a less-suspicious null result on a plausible-sounding hypothesis could easily be misread as a ruled-out cause. This should be a hard validation error, the same way the regex case is, not a quiet empty result.

### 6. Direct link from an Error Tracking issue to correlated payload-capture attributes

I had `custom.issue.id`/`custom.issue.first_seen`/`custom.issue.first_seen_version` available on spans, which is genuinely useful (issue-level onset timing, independent of payload capture). But there's no bridge from "here's an Error Tracking issue" to "here's what's statistically different about the payloads on spans tagged with this issue vs. spans without it." That bridge — essentially #2, but scoped to an issue ID instead of a raw query — would turn Error Tracking from a grouping/dedup tool into a genuine root-cause tool for payload-driven errors.

## Part 2 — How easy was it to query captured Lambda payloads?

Honest answer: **moderate, with sharp edges** — not "hard to find," but "easy to get an unhelpful or misleading result without noticing."

What worked well:
- Once I knew the attribute path, restricting `search_datadog_spans` via `custom_attributes` to exactly the fields I cared about was straightforward and kept results (relatively) small.
- The wildcard hedge (`custom_attributes: ["*"]`) as a first broad pull, before narrowing, was a reasonable and necessary discovery step given there's no schema-listing tool (see #3 above) — but it's a workaround for a missing capability, not a good primary workflow.

What was sharp-edged:
- **No schema discovery.** I had to pull a full unrestricted sample just to learn the attribute path existed and what shape it had. This is the single biggest ease-of-use gap — see #3.
- **Token-limit auto-fallback-to-file is silent about *why* it's necessary.** When a `search_datadog_spans` call is too large, results get dumped to a local file and I'm told to grep it locally. That's a reasonable mechanism, but it means the moment payload capture is involved (payloads are often large, nested JSON blobs), a plain sample pull is very likely to blow the inline budget — pushing every payload-based investigation toward "export and grep locally" as the default mode rather than the exception. A tighter default (e.g., "if `custom_attributes` isn't set, and the service has payload capture enabled, truncate each payload to N bytes in the response with a note, rather than truncating the whole response set") would keep more investigations single-call.
- **No aggregation over nested/captured fields (see Part 1, #1).** This is really the crux: querying *individual* payloads was fine; querying the *statistical shape* of payloads across many spans was not supported at all, and that's usually the actually-useful question in an incident (one anomalous payload is noise; a population-level shift is signal).
- **No redaction/sensitivity guidance surfaced in-tool.** Not a friction point I hit directly, but worth naming: when recommending "turn on payload capture" as a fix for future incidents (as I did in the earlier "no payload capture" retrospective), the tooling itself gives no indication of what's captured, whether scrubbing rules are active, or how to test a scrubbing rule before enabling capture broadly. That's a gap in confidence for the *recommendation*, not just the *investigation*.

## Why these improvements matter, concretely

Every one of the four proposed improvements maps to a specific moment in this investigation where I was farther from the answer than the data actually was:

| Gap | Cost paid this incident | What it would have bought |
|---|---|---|
| No nested-attribute regex/shape aggregation | 2 raw sample pulls + local grep/awk instead of 1 API call | Faster, and statistically confident (full population, not a sample) rather than eyeballed |
| No log-style pattern clustering over payload values | Had to already hypothesize "digit-count drift" before I could test for it | Proactive discovery of the anomalous shape with no upfront hypothesis — arguably the fastest possible path to this root cause |
| No schema discovery for nested payload attributes | 1 extra broad/wildcard sample pull just to learn the attribute path | Faster initial orientation, less guessing |
| Silent empty result on malformed `group_by` | Had to notice "0 buckets" was suspicious rather than getting a clear error | Removes a specific way to be *wrongly confident* a hypothesis is ruled out |
| No issue-to-payload-shape bridge | Not directly hit this incident, but would generalize the fix above to Error Tracking's normal workflow | Turns Error Tracking into a root-cause tool for payload-driven errors, not just a dedup/grouping tool |

None of these are exotic asks — they're the difference between "you can see the payload if you already know exactly what you're looking for" and "you can ask a statistical question about the payload and trust the answer," which is the actual shape of most real incidents.

## Part 3 — The SSM parameter change: a blind spot outside payload capture entirely

The AWS-CLI sub-agent's actual root cause wasn't found in Datadog at all — it was found via `aws ssm get-parameter` (and, presumably, SSM's parameter history / CloudTrail), which surfaced that `/rey/payload-capture/format-generation` was manually flipped from `stable` to `next` at a specific timestamp. This is worth calling out on its own, separate from the payload-capture discussion above, because it's a different *category* of blind spot: not "the data was there but hard to query," but "the data wasn't surfaced in Datadog at all."

**Does SSM data get pulled into Datadog today?**

To my knowledge, only partially, and not in a form that would have surfaced this:

- **Metrics:** AWS Systems Manager Parameter Store does not publish CloudWatch metrics for parameter reads/writes/value-changes at all — there's nothing for Datadog's standard AWS integration (which works by polling CloudWatch metric namespaces) to pull, regardless of integration configuration. This isn't a Datadog gap; it's an AWS-side gap. Metrics are not a viable path for this signal.
- **Logs:** SSM API calls (`PutParameter`, `DeleteParameter`, `LabelParameterVersion`, etc.) are recorded as CloudTrail management events, and CloudTrail logs *can* be ingested into Datadog Log Management if the customer has set up CloudTrail log collection (via S3/Kinesis Firehose forwarding, per Datadog's standard log pipeline). So the raw event is capturable — but only if that log pipeline is explicitly configured, and even then it lands as an undifferentiated log line in Log Management, not as a first-class, timeline-visible "config change" event correlated to the services that read that parameter.
- **Change Tracking:** `get_change_stories` supports a `configuration` story type in principle, which is the natural home for this kind of event — but in this account it returned empty for both services across every window I checked (see the original incident writeup's dead-end log). Whether that's because CloudTrail/Config-based configuration tracking isn't wired up for this account, or because SSM parameter changes specifically aren't a supported source for the `configuration` story type, I could not determine from the tools available to me — it's a real open question, not something I could verify either way. Either way, from the investigator's seat, the effect was the same: this class of change was invisible to the tool built for exactly this purpose.

**Why this class of change is structurally easy to miss**

Even a fully-instrumented deployment-tracking setup (the kind that would catch "a new Lambda version was published" or "a new ECS task def was rolled out") would *not* have caught this, because it's not a deploy — it's a runtime configuration read. `rey-settlement-producer`'s behavior changed without any code change, container rebuild, or Lambda version bump; it just started reading a different value from Parameter Store on its next invocation. Any change-tracking model built around deploy events (version diffs, image tags, git SHAs) has a structural blind spot for "the code didn't change, but the config it reads at runtime did."

**Proposed improvement: first-class runtime-config-change tracking, correlated to the services that consume it**

1. **Ingest SSM (and Secrets Manager, and AppConfig) parameter-change events as a native Change Tracking source**, not as generic CloudTrail logs that happen to be searchable. Concretely: a `configuration` story type entry with the parameter name, old/new value (redacted/hashed if the parameter is a SecureString or matches a sensitivity pattern), the IAM principal that made the change, and the timestamp — sourced directly from CloudTrail's `PutParameter` event (which does include the new value in `requestParameters` for standard/non-secure parameters) rather than requiring the customer to build their own log-based detection.
2. **Correlate parameter reads to consuming services automatically.** Datadog already has APM traces showing `rey-settlement-producer` (presumably) calling `ssm:GetParameter` for this parameter — if AWS SDK spans for SSM calls are captured (as they likely are for any service using X-Ray/Datadog Lambda instrumentation with AWS SDK auto-instrumentation), Datadog could build the same kind of dependency edge it builds for "service A calls service B" for "service A reads parameter P," and then surface "parameter P changed" directly on service A's service page timeline — the same visual slot deploy markers already occupy. This turns an invisible cross-cutting config change into the same kind of "something changed right when errors started" signal a deploy marker gives you today.
3. **Surface parameter-change markers on the trace/error timeline of any service observed reading that parameter**, the same way deploy markers already overlay on latency/error graphs. This is the single highest-value version of this idea: I already know how to *read* a deploy marker lined up with an error spike (I used exactly that pattern-matching instinct throughout this incident) — the same visual affordance for "config value changed here" would have let this incident resolve in Datadog directly, without needing an AWS-CLI-capable sub-agent at all.

**Why this matters:** the entire distinction I made in the earlier retrospective ("with payload capture I found *what* was wrong, but not *why* it changed") was actually two separate blind spots at once — one in payload/data visibility (addressed in Parts 1–2 above), and one in runtime-configuration-change visibility, which sits entirely outside the payload-capture discussion and outside code-deploy-based change tracking as it exists today. Closing the second gap would have plausibly let the *entire* investigation — cause and mechanism both — happen without leaving Datadog or invoking AWS CLI at all.
