import boto3
import json
import os

from datadog_lambda.metric import lambda_metric
from ddtrace import tracer

client = boto3.client('sqs')
queue_url = os.environ['PYTHON_SQS_QUEUE_URL']
runtime = os.environ['AWS_EXECUTION_ENV']

def producer(event, context):
    trace_id = _current_trace_id()
    msg = json.dumps({
            'runtime': runtime,
            'trace_id': trace_id,
    })
    print(f'sending sqs message {msg}')
    client.send_message(QueueUrl=queue_url, MessageBody=msg)
    return {'statusCOde': 200, 'body': 'ok'}

def consumer(event, context):
    trace_id = _current_trace_id()
    for record in event['Records']:
        payload = json.loads(record['body'])
        print(f'received sqs message {payload}')
        lambda_metric('trace_context.propagated.sqs', 1, tags=[
                f'consumer_rumtime:{runtime}',
                f'producer_runtime:{payload["runtime"]}',
                f'success:{trace_id == payload["trace_id"]}',
                f'transport:sqs',
        ])

def _current_trace_id():
    ctx = tracer.current_trace_context()
    assert ctx, 'no trace context found!'
    print(f'found trace context {ctx}')
    return ctx.trace_id
