# Dashboard: `rey-storefront` order pipeline

This walks through building a monitoring dashboard for the storefront pipeline
by hand, from a cold start — you just turned on payload capture for a new
service and want to know what you have. That's deliberate: this exercise
doubles as a live check of today's Datadog capability against "schema
discovery." Expect Section 0 below to feel manual. That's the point — it's
exactly the gap the two `rey-settlement-processor` retrospectives called out.

Widgets are numbered 1–20 and grouped into 3 sections. A layout drawing is at
the bottom.

## Section 0 — Prerequisite: create facets

There is no schema-discovery API today, so before any widget below can group
or filter on a nested payload attribute, you need to manually create a facet
for it.

1. Send some traffic (`npm run invoke`, then `npm run on`).
2. Open [APM Trace Explorer](https://app.datadoghq.com/apm/traces),
   filter to `service:rey-storefront-processor`, and open one span.
3. Expand the captured request payload and confirm what you're looking at
   first: **check whether the SQS body is flattened into individually
   addressable attributes** (`function.request.Records.0.body.store`,
   `...body.order.id`, etc.) **or stays a single opaque JSON string**
   (`function.request.Records.0.body`) — this depends on the tracer version
   and isn't guaranteed. If it's a single string, none of the faceted widgets
   below (Sections 1–2) will work; skip to the List Stream widget in Section 3
   as your fallback and treat that as itself a finding worth writing down.
4. If it is flattened, create a facet for each attribute path below, either
   via "Create Facet" on the tag directly in the trace side panel, or in bulk
   under Settings → APM → Manage Facets.

Facet paths (relative to `function.request.Records.0.body`):

| path | notes |
|---|---|
| `store` | enum |
| `channel` | enum |
| `customer.id` | high cardinality |
| `customer.loyaltyTier` | enum |
| `customer.firstOrder` | boolean |
| `order.id` | high cardinality |
| `order.fulfillmentType` | enum, derived |
| `order.totalCents` | numeric |
| `order.lineItems.0.category` | **array-index caveat**: only the first line item is addressable this way |
| `order.lineItems.0.sku` | high cardinality, same array-index caveat |
| `payment.method` | enum |
| `payment.giftCardApplied` | boolean |
| `shipping.method` | used below as a presence proxy for the sparse `shipping` object |
| `shipping.address.country` | only present on non-digital orders |
| `device.ip` | high cardinality |
| `device.sessionId` | high cardinality |
| `experiments.0.name` | sparse array + array-index caveat |

## Section 1 — Service health

A `group` widget titled **"Service Health"** containing:

1. **Query Value** — producer invocations, last 1h. Query:
   `service:rey-storefront-producer` → count of spans.
2. **Query Value** — processor invocations, last 1h. Query:
   `service:rey-storefront-processor` → count of spans.
3. **Query Value** — processor error rate, last 1h. 2-query formula:
   `query1/query2*100` where query1 = `service:rey-storefront-processor
   status:error` count, query2 = `service:rey-storefront-processor` count.
   Expect ≈0% — this app has no error path.
4. **Query Value** — DLQ depth. Metric
   `aws.sqs.approximate_number_of_messages_visible` filtered to
   `queuename:rey-storefront-orders-dlq`. Expect ≈0.
5. **Timeseries** — orders processed per minute. Query:
   `service:rey-storefront-processor` → count, rollup by 1m.
6. **Timeseries** — processor latency. Query:
   `service:rey-storefront-processor` → p50 and p95 of `@duration`, two lines
   on one graph.

## Section 2 — Schema & attribute discovery

A `group` widget titled **"Schema & Attribute Discovery"** — this is the core
of the exercise. Each widget answers a version of "what does this field
actually look like?"

**Toplists (enum / low-cardinality discovery — what values exist and how
often):**

7. Toplist — orders by `channel`
8. Toplist — orders by `store`
9. Toplist — orders by `customer.loyaltyTier`
10. Toplist — orders by `payment.method`
11. Toplist — orders by `order.fulfillmentType`

**Query Values, distinct count (cardinality awareness — is this field an
enum I can facet on, or an ID I shouldn't):**

12. Query Value — distinct count of `customer.id`, last 1h
13. Query Value — distinct count of `order.lineItems.0.sku`, last 1h
14. Query Value — distinct count of `device.ip`, last 1h

**Query Values, % present (sparse-field visibility — which fields are
always there vs. only sometimes; each is a 2-query formula `query1/query2*100`):**

15. Query Value — % of orders with `shipping.method:*` present (query1 =
    `service:rey-storefront-processor shipping.method:*`, query2 = all
    processor spans)
16. Query Value — % of orders with a `order.promotions` entry present
    (same pattern, filter on the promotions facet if created, or
    `order.discountCents:>0` as a proxy)
17. Query Value — % of orders with an `experiments.0.name:*` entry present

**Query Table (2-dimensional shape):**

18. Query Table — `store` × `order.fulfillmentType` cross-tab, count of orders
    in each cell. This is the kind of question ("how does this field's
    distribution vary by that other field") that today requires either a
    facet-grouped table or pulling raw payloads and cross-tabbing by hand.

## Section 3 — Raw inspection & caveats

A `group` widget titled **"Raw Inspection & Caveats"** containing:

19. **List Stream**, `data_source: trace_stream`, query
    `service:rey-storefront-processor`, sorted newest-first. This is the
    manual fallback for eyeballing an actual captured payload — and the
    widget to lean on if Section 0's facets don't pan out (single opaque JSON
    string, or nested attributes not flattening the way you expected).
20. **Note** widget, short text covering:
    - Every facet in Section 0 had to be created by hand — there's no
      schema-discovery API to enumerate them for you.
    - Only the first element of an array is reliably addressable
      (`lineItems.0.*`, `experiments.0.*`) — a 3-item order and a 1-item order
      look identical on those facets.
    - Datadog's existing Log Patterns feature (`logs_pattern_stream`) clusters
      *log* message shapes, but has no equivalent for span/payload attribute
      values — which is exactly the "payload-value pattern clustering" gap
      the `rey-settlement-processor` retrospectives called out.

## Layout drawing

12-column dashboard grid. Widget numbers refer to the list above; sizes are
approximate (width × height in grid units).

```
┌─ GROUP: Service Health ─────────────────────────────────────────────────────┐
│ ┌────────┬────────┬────────┬────────┐  ┌───────────────┬───────────────┐   │
│ │ 1  QV  │ 2  QV  │ 3  QV  │ 4  QV  │  │ 5  Timeseries │ 6  Timeseries │   │
│ │ 3w×2h  │ 3w×2h  │ 3w×2h  │ 3w×2h  │  │   6w×3h       │   6w×3h       │   │
│ └────────┴────────┴────────┴────────┘  └───────────────┴───────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ GROUP: Schema & Attribute Discovery ────────────────────────────────────────┐
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┐                    │
│ │ 7 Toplist│ 8 Toplist│ 9 Toplist│10 Toplist│11 Toplist│  channel / store /  │
│ │  channel │  store   │  tier    │  method  │fulfilltyp│  tier / method /   │
│ │                                                       │  fulfillmentType   │
│ │        each ~2.4w × 3h (5 across a 12-col row)        │                    │
│ └──────────┴──────────┴──────────┴──────────┴──────────┘                    │
│ ┌────────────┬────────────┬────────────┐  ┌────────────┬────────────┬─────┐ │
│ │12 QV       │13 QV       │14 QV       │  │15 QV %     │16 QV %     │17 QV%│ │
│ │distinct    │distinct    │distinct    │  │shipping    │promo       │exp   │ │
│ │customers   │skus        │IPs         │  │present     │present     │pres. │ │
│ │        each 4w×2h                       │        each 4w×2h              │ │
│ └────────────┴────────────┴────────────┘  └────────────┴────────────┴─────┘ │
│ ┌───────────────────────────────────────────────────────────────────────┐   │
│ │ 18  Query Table — store × fulfillmentType crosstab       (12w × 4h)   │   │
│ └───────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ GROUP: Raw Inspection & Caveats ────────────────────────────────────────────┐
│ ┌───────────────────────────────────────────────────────┐  ┌───────────────┐│
│ │ 19  List Stream (trace_stream) — raw captured payloads │  │ 20  Note      ││
│ │      service:rey-storefront-processor       (9w × 6h)  │  │  caveats      ││
│ │                                                         │  │  (3w × 6h)    ││
│ └───────────────────────────────────────────────────────┘  └───────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```
