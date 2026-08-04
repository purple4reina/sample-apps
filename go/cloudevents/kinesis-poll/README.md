# CloudEvents over Kinesis — locally-polled consumer

Same repro as `../kinesis` (dd-trace-go#5107), but the consumer isn't a
Lambda — it's a plain Go program you run on your machine that pulls records
straight off the stream with `GetShardIterator`/`GetRecords`. Useful when the
customer's consumer isn't Lambda-triggered at all.

- `producer/` — a Lambda, deployed via `serverless.yml`. Its Kinesis client is
  instrumented with dd-trace-go's AWS SDK v2 middleware, which splices a
  top-level `"_datadog"` key into the record body to propagate trace/DSM
  context (see `dd-trace-go/contrib/aws/aws-sdk-go-v2/internal/kinesis/kinesis.go`).
- `consumer/` — a standalone Go binary with no Datadog instrumentation at all.
  It polls the stream directly and decodes each record as a CloudEvent, so the
  only source of the extra `_datadog` property is the producer.

## Why decoding fails

The CloudEvents SDK's JSON decoder treats any unrecognized top-level key as a
CloudEvents extension attribute, and extension names may only contain ASCII
letters and digits. `_datadog`'s underscore fails that validation, so
`json.Unmarshal` into a CloudEvents `Event` returns an error.

## Deploy the producer

```
cd producer
npm install
./build_deploy.sh
```

## Run the consumer locally

```
cd consumer
export KINESIS_STREAM_NAME=rey-go-cloudevents-kinesis-poll-dev  # match serverless.yml's stage
go run .
```

Requires AWS credentials in your environment (e.g. `aws-vault exec ... -- go run .`).

## Reproduce

1. Invoke the `producer` function URL (see `serverless info` for the URL, run
   from `producer/`) with an empty body — it builds a hello-world CloudEvent
   and PUTs it to Kinesis via the instrumented client.
2. Watch the running `consumer` process — it will log
   `failed to decode CloudEvent from record ...: bad key, CloudEvents
   attribute names MUST consist of lower-case letters ('a' to 'z'), upper-case
   letters ('A' to 'Z') or digits ('0' to '9') from the ASCII character set`.
