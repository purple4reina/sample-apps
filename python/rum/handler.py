import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(event),
    }

def authorizer(event, context):
    print(event)
    if event.get('type') == 'REQUEST':
        token = (event.get('headers') or {}).get('Authorization', '')[7:]  # Skip 'Bearer '
        method_arn = event.get('methodArn')
    else:
        token = event.get('authorizationToken', '')[7:]
        method_arn = event.get('methodArn')
    return {
        'principalId': 'user',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow' if token else 'Deny',
                    'Resource': [method_arn or '*'],
                }
            ]
        }
    }
