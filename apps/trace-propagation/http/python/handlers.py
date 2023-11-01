import base64
import json
import requests
import os

from datadog_lambda.metric import lambda_metric
from ddtrace import tracer

server_urls = os.environ.get('SERVER_URLS', '').split(',')
runtime = os.environ.get('AWS_EXECUTION_ENV', '').replace('AWS_Lambda_', '')

def client(event, context):
    data = json.dumps({
            'runtime': runtime,
            'trace_id': _current_trace_id(),
    })
    for url in server_urls:
        print(f'calling {url} with data {data}')
        requests.get(url, data=data)
    return {'statusCode': 200, 'body': 'ok'}

def server(event, context):
    trace_id = _current_trace_id()
    body = event.get('body')
    print(f'received http event body {body}')
    payload = json.loads(base64.b64decode(body))
    print(f'received http data {payload}')
    lambda_metric('trace_context.propagated.http', 1, tags=[
            f'client_runtime:{runtime}',
            f'server_runtime:{payload.get("runtime")}',
            f'success:{trace_id == payload.get("trace_id")}',
            f'transport:http',
    ])
    return {'statusCode': 200, 'body': 'ok'}

def _current_trace_id():
    ctx = tracer.current_trace_context()
    assert ctx, 'no trace context found!'
    print(f'found trace context {ctx}')
    return str(ctx.trace_id)
