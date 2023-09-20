import boto3
import json
import os

from datadog_lambda.metric import lambda_metric
from ddtrace import tracer

client = boto3.client('sns')
topic_arns = os.environ['SNS_TOPIC_ARNS'].split(',')
runtime = os.environ['AWS_EXECUTION_ENV'].replace('AWS_Lambda_', '')

def producer(event, context):
    msg = json.dumps({
            'runtime': runtime,
            'trace_id': _current_trace_id(),
    })
    for arn in topic_arns:
        print(f'sending sns-sqs message {msg} to {arn}')
        client.publish(TopicArn=arn, Message=msg)
    return {'statusCode': 200, 'body': 'ok'}

def consumer(event, context):
    trace_id = _current_trace_id()
    for record in event['Records']:
        body = json.loads(record['body'])
        msg = json.loads(body['Message'])
        print(f'received sns-sqs message {msg}')
        lambda_metric('trace_context.propagated.sns-sqs', 1, tags=[
                f'consumer_runtime:{runtime}',
                f'producer_runtime:{msg.get("runtime")}',
                f'success:{trace_id == msg.get("trace_id")}',
                f'transport:sns-sqs',
        ])

def _current_trace_id():
    ctx = tracer.current_trace_context()
    assert ctx, 'no trace context found!'
    print(f'found trace context {ctx}')
    return str(ctx.trace_id)
