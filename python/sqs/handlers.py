import boto3
import os

client = boto3.client('sqs')
queue_url = os.environ['SQS_QUEUE_URL']

def producer(event, context):
    print(f'sending sqs message to {queue_url}')
    client.send_message(QueueUrl=queue_url, MessageBody='Hello Rey!')
    return 'ok'

def consumer(event, context):
    for record in event['Records']:
        print(f'received sqs message {record}')
