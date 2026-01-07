import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(event),
    }

def authorizer(event, context):
    token = event['authorizationToken']
    method_arn = event['methodArn']

    if token == "allow":
        effect = "Allow"
    else:
        effect = "Deny"

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": method_arn
            }
        ]
    }

    return {
        'principalId': 'user',
        'policyDocument': policy_document
    }
