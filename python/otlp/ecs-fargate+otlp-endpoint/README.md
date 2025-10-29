# README

## Sending data to staging

1. Trace endpoint: https://trace.agent.datad0g.com/api/v0.2/traces
2. Set `dd-source` to `datadog`
3. Find an api key from https://dd.datad0g.com/
  - `OTLP_Trace_Endpoint_Serverless` is a good choice
  - Change `DD_API_KEY` in `lib/ecs-fargate+otlp-endpoint-stack.ts` to the new value
