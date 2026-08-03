# User stories for proposed Datadog payload-capture API improvements

## Context

Two retrospectives on the `rey-settlement-processor` incident propose Datadog API/tooling
improvements for querying captured Lambda payloads (nested-attribute aggregation/regex,
payload-value pattern clustering, schema discovery, field projection, population-diff,
Error Tracking correlation, config-change tracking). All of that was framed around
*incident debugging*. These 3 stories show a customer wanting one of these capabilities
during **normal operations** — not while firefighting — to help scope the roadmap for
the first new feature in this project, alongside the incident itself.

## User stories

### 1. Schema discovery — onboarding a new service to payload capture
**Persona:** Platform/data engineer enabling payload capture on a newly migrated Lambda service.

**Story:** "As a platform engineer turning on payload capture for a new service, I want to
list the distinct nested attribute keys actually appearing on that service's spans (with
sample values and observed cardinality), so I can build my first dashboards and alerts
without blindly pulling a wildcard sample and reverse-engineering the JSON shape by eye."

**Maps to doc gap:** "no schema discovery" (both retrospectives) — turns a one-off
incident workaround into a routine onboarding step.

### 2. Payload-shape drift monitor — proactive data-quality guardrail
**Persona:** SRE/on-call owner of a payment-adjacent service who wants early warning of
upstream format changes, before they cause errors.

**Story:** "As an SRE, I want a scheduled check that clusters the shape (character-class +
length signature) of a specific payload field — e.g. `settlement.ref` — over the last 24h
and alerts me when a new shape cluster appears or an existing cluster's share shifts
significantly, so I find out about a partner's format change the same day it starts
rolling out, instead of when error volume spikes."

**Maps to doc gap:** "log-style pattern clustering extended to payload values" +
"silent-failure group_by" (a drift monitor is worthless if malformed queries silently
return zero results). This is the same clustering machinery as the incident, but run as
a standing guardrail rather than a reactive lookup.

### 3. Business/rollout metrics dashboard — field projection + aggregation
**Persona:** Product engineer tracking adoption of an intentional, in-flight format
migration (e.g. counterparty IDs moving from a legacy scheme to a new one over a phased
rollout).

**Story:** "As a product engineer running a phased migration, I want a dashboard that
shows, per day, what fraction of events have the new vs. old counterparty-ID format —
built by aggregating one projected nested field across weeks of traffic — without each
query pulling full SQS payload blobs (receipt handles, infra tags, etc.) that blow past
response size limits and slow the dashboard down."

**Maps to doc gap:** nested-attribute aggregation (both retrospectives) + field
projection on `custom_attributes` (Bits Debug) — used here for steady-state BI/reporting,
not debugging.

## Why these three are diverse

- (1) is a one-time, exploratory *discovery* need at service-onboarding time.
- (2) is a continuous, *statistical/alerting* need with no operator in the loop until it fires.
- (3) is a recurring, *reporting/dashboard* need driven by product rather than reliability.

Together with the incident's reactive "explain what already broke" use case, these span
the lifecycle: onboarding → continuous monitoring → business reporting → incident response.
