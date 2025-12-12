service: rey-python-lambda

provider:
  name: aws
  region: sa-east-1
  runtime: python3.12
  environment:
    DD_API_KEY: ${env:DD_API_KEY}
    DD_CAPTURE_LAMBDA_PAYLOAD: false
    DD_ENV: dev
    DD_EXTENSION_VERSION: next
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
  {{- range coll.Slice 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 }}
  {{ . }}:
    handler: datadog_lambda.handler.handler
    url: true
    layers:
      - arn:aws:lambda:sa-east-1:464622532012:layer:Datadog-Python312:{{ .  }}
      - arn:aws:lambda:sa-east-1:464622532012:layer:Datadog-Extension:90
  {{- end }}
