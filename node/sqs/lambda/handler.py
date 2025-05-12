import boto3
import json
import os

sqs_client = boto3.client('sqs')
sqs_queue_url = os.environ.get('SQS_QUEUE_URL')

def handle(event, context):
    evt = json.dumps(event)
    print(f"Received event: {evt}")
    if sqs_queue_url is not None:
        print(f"Sending message to SQS queue: {sqs_queue_url}")
        sqs_client.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps('{"hello":"world"}'),
        )
    return evt

if __name__ == '__main__':
    handle({}, {})
