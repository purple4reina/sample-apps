from aws_lambda_context import (
        LambdaClientContext,
        LambdaClientContextMobileClient,
        LambdaCognitoIdentity,
        LambdaContext,
)

_lambda_cognito_identity = LambdaCognitoIdentity()
_lambda_cognito_identity.cognito_identity_id = 'cognito_identity_id'
_lambda_cognito_identity.cognito_identity_pool_id = 'cognito_identity_pool_id'

_lambda_client_context_mobile_client = LambdaClientContextMobileClient()
_lambda_client_context_mobile_client.installation_id = 'installation_id'
_lambda_client_context_mobile_client.app_title = 'app_title'
_lambda_client_context_mobile_client.app_version_name = 'app_version_name'
_lambda_client_context_mobile_client.app_version_code = 'app_version_code'
_lambda_client_context_mobile_client.app_package_name = 'app_package_name'

_lambda_client_context = LambdaClientContext()
_lambda_client_context.client = _lambda_client_context_mobile_client
_lambda_client_context.custom = {'custom': True}
_lambda_client_context.env = {'env': 'test'}

lambda_context = LambdaContext()
lambda_context.function_name = 'function_name'
lambda_context.function_version = 'function_version'
lambda_context.invoked_function_arn = 'invoked_function_arn'
lambda_context.memory_limit_in_mb = 'memory_limit_in_mb'
lambda_context.aws_request_id = 'aws_request_id'
lambda_context.log_group_name = 'log_group_name'
lambda_context.log_stream_name = 'log_stream_name'
lambda_context.identity = _lambda_cognito_identity
lambda_context.client_context = _lambda_client_context
