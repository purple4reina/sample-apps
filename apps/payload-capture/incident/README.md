# payload-capture

EventBridge → Producer Lambda → SQS → Processor Lambda (Datadog payload capture enabled)

A small settlement-processing pipeline. A producer emits synthetic settlement
messages onto a queue on a one-minute schedule; a processor consumes them one at
a time and settles them. Both functions are instrumented with the Datadog Lambda
extension and have request/response **payload capture** turned on, so every
invocation's payload is available on its `aws.lambda` span.

The pipeline ships in a healthy state and can be switched into a failing state
(and back) at any time with a single command — see [Healthy ⇄ failing](#healthy--failing).

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

## Traffic

Traffic starts automatically after deploy: the producer runs every minute. To
also fire a run on demand:

```
$ aweserv npm run invoke
```

## Healthy ⇄ failing

```
$ aweserv npm run drift    # move the upstream into its next state
$ aweserv npm run heal     # restore the upstream to its original state
```

Changes take effect on the next scheduled producer run (within ~1 minute).

## Observe in Datadog

Look at the `rey-settlement-processor` service in
[Serverless](https://app.datadoghq.com/functions) and the
[Trace Explorer](https://app.datadoghq.com/apm/traces) (`service:rey-settlement-processor`).
Open a failing invocation to see its captured request payload on the span.

## Destroy

```
$ aweserv npm run destroy
```
