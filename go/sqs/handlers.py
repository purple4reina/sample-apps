import boto3
import json
import os

from ddtrace import tracer

client = boto3.client('sqs')
queue_url = os.environ['SQS_QUEUE_URL']
runtime = os.environ['AWS_EXECUTION_ENV'].replace('AWS_Lambda_', '')

def producer(event, context):
    msg = json.dumps({
            'runtime': runtime,
            'trace_id': _current_trace_id(),
    })
    print(f'sending sqs message {msg} to {queue_url}')
    client.send_message(QueueUrl=queue_url, MessageBody=msg)
    return {'statusCode': 200, 'body': 'ok'}

def _current_trace_id():
    ctx = tracer.current_trace_context()
    assert ctx, 'no trace context found!'
    print(f'found trace context {ctx}')
    return str(ctx.trace_id)
