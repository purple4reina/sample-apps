service: rey-python-lambda

provider:
  name: aws
  region: sa-east-1
  runtime: python3.12
  environment:
    DD_API_KEY: ${env:DD_API_KEY}
    DD_CAPTURE_LAMBDA_PAYLOAD: false
    DD_ENV: dev
    DD_LAMBDA_HANDLER: handler.handler
    DD_LOGS_INJECTION: false
    DD_MERGE_XRAY_TRACES: false
    DD_SERVERLESS_LOGS_ENABLED: true
    DD_SERVICE: rey-python-lambda
    DD_TRACE_ENABLED: true

package:
  patterns:
    - '!**'
    - 'handler.py'

functions:
  {{- range $version := seq 60 90 }}
  {{- range $mode := coll.Slice "next" "compatibility" }}
  {{ $version }}-{{ $mode }}:
    handler: datadog_lambda.handler.handler
    url: true
    layers:
      - arn:aws:lambda:sa-east-1:464622532012:layer:Datadog-Python312:120
      - arn:aws:lambda:sa-east-1:464622532012:layer:Datadog-Extension:{{ $version  }}
    environment:
      DD_EXTENSION_VERSION: {{ $mode }}
  {{- end }}
  {{- end }}
