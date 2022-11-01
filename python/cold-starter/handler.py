import boto3
import datetime
import json
import os

coldstart_fns = os.environ.get('REY_COLD_START_FNS').split(',')

client = boto3.client('lambda')

def handler(event, context):
    now = datetime.datetime.now()
    responses = {}
    exceptions = {}

    for fn in coldstart_fns:
        try:
            response = client.update_function_configuration(
                    FunctionName=fn,
                    Description=f'last cold start at {now}',
            )
            responses[fn] = response
        except Exception as e:
            exceptions[fn] = f'[{e.__class__.__name__}] {str(e)}'

    return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(coldstart_fns),
                'exceptions': exceptions,
                'responses': responses,
            }),
    }
