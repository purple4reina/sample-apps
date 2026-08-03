# onboarding

EventBridge (schedule OFF by default) → Producer Lambda → SQS → Processor Lambda
(Datadog payload capture enabled)

A small storefront order-processing pipeline. A producer emits synthetic
`order.placed` events onto a queue; a processor consumes them one at a time.
Both functions are instrumented with the Datadog Lambda extension and have
request/response **payload capture** turned on, so every invocation's payload
is available on its `aws.lambda` span. Unlike the `incident/` app, this one
never fails and never drifts — it's meant to produce a steady stream of rich,
realistic payloads to explore, as a stand-in for turning payload capture on
for a brand-new service.

## Prerequisites

- Node.js 18+ and the AWS CDK (`npm i` installs a local `aws-cdk`).
- AWS credentials for the serverless sandbox. The examples below use `aweserv`
  (the `aws-vault exec sso-serverless-sandbox-account-admin --` alias); use
  whatever wrapper provides your credentials.
- A Datadog API key exported as `DD_API_KEY` (and optionally `DD_SITE`,
  default `datadoghq.com`) before deploying.

## Deploy

```
$ npm install
$ export DD_API_KEY=<your-datadog-api-key>
$ aweserv npm run deploy
```

Deploys to `sa-east-1`. If this account has not been CDK-bootstrapped, run
`aweserv npx cdk bootstrap` first.

**Traffic is OFF by default.** The stack deploys with the producer's schedule
disabled, so nothing runs until you turn it on (see below).

## Sanity check

Before turning on continuous traffic, fire a single producer run and confirm
it works end to end:

```
$ aweserv npm run invoke
```

This emits one batch of orders. Give it a minute, then look for a trace on
`service:rey-storefront-processor` in [APM Trace
Explorer](https://app.datadoghq.com/apm/traces).

## Turn traffic on / off

```
$ aweserv npm run on     # producer runs every minute
$ aweserv npm run off    # stop new orders (anything already queued still drains)
```

Both act on the `rey-storefront-producer-schedule` EventBridge rule directly —
no redeploy needed. One caveat: redeploying the stack (`cdk deploy`) resets
the rule back to disabled, so re-run `npm run on` after any redeploy.

## Observe in Datadog

Look at `rey-storefront-producer` and `rey-storefront-processor` in
[Serverless](https://app.datadoghq.com/functions) and the [Trace
Explorer](https://app.datadoghq.com/apm/traces)
(`service:rey-storefront-processor`). Open a processor invocation's span and
expand its captured request payload — it's the SQS message body, under
`function.request.Records.0.body`.

## What's in the payload

Each event is an `order.placed` event with 3+ levels of nesting: a customer,
an order (with an array of line items and optional promotions), payment info,
an optional shipping block, device info, and optional experiment assignment.
Several fields are enums (`store`, `channel`, `payment.method`, ...), some are
genuinely high-cardinality (`customer.id`, `device.ip`, ...), and a few are
sparse — present only some of the time, in some cases driven by a business
rule (`shipping` is present iff the order isn't fully digital). See
`src/producer/order.js` for the exact shape and rules.

This variety is the point: [`DASHBOARD.md`](./DASHBOARD.md) walks through
building a monitoring dashboard for this service from scratch, using the
captured payload to answer "what does this data actually look like?"

## Destroy

```
$ aweserv npm run destroy
```
