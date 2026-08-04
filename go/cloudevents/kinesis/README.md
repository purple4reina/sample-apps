# CloudEvents over Kinesis — dd-trace-go#5107 repro

Reproduces https://github.com/DataDog/dd-trace-go/issues/5107: a CloudEvents
payload sent through a Datadog-instrumented Kinesis `PutRecord` call fails to
decode on the consumer side.

## Why it fails

dd-trace-go's AWS SDK v2 instrumentation
(`contrib/aws/aws-sdk-go-v2/internal/kinesis/kinesis.go`) injects trace/DSM
context into every JSON-object Kinesis record body by splicing in a top-level
`"_datadog"` key. The CloudEvents SDK's JSON decoder treats unrecognized
top-level keys as CloudEvents extension attributes, and extension names may
only contain ASCII letters and digits — `_datadog`'s underscore fails that
validation, so `json.Unmarshal` into a CloudEvents `Event` returns an error.

## Deploy

```
npm install
./build_deploy.sh
```

## Reproduce

1. Invoke the `producer` function URL (see `serverless info` for the URL) with
   an empty body — it builds a hello-world CloudEvent and PUTs it to the
   Kinesis stream via the instrumented client.
2. Check the `consumer` function's CloudWatch logs — it will log
   `failed to decode CloudEvent from record ...: bad key, CloudEvents
   attribute names MUST consist of lower-case letters ('a' to 'z'),
   upper-case letters ('A' to 'Z') or digits ('0' to '9') from the ASCII
   character set`.
