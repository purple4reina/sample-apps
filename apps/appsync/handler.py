import json

def handler(event, context):
    return json.dumps({
            'event': event,
            'context': {
                'function_name': context.function_name,
                'memory_limit_in_mb': context.memory_limit_in_mb,
                'invoked_function_arn': context.invoked_function_arn,
                'aws_request_id': context.aws_request_id,
                'log_group_name': context.log_group_name,
                'log_stream_name': context.log_stream_name,
                'identity': {
                    'cognito_identity_id': context.identity.cognito_identity_id,
                },
                'client_context': context.client_context,
            },
    }, indent=2)
