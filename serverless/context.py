class Context(object):
    function_name = 'my_function_name'
    function_version = 'my_function_version'
    invoked_function_arn = 'my_invoked_function_arn'
    memory_limit_in_mb = 128
    aws_request_id = 'my_aws_request_id'
    log_group_name = 'my_log_group_name'
    log_stream_name = 'my_log_stream_name'

    def get_remaining_time_in_millis(self):
        return 0

    class identity(object):
        cognito_identity_id = 'my_cognito_identity_id'
        cognito_identity_pool_id = 'my_cognito_identity_pool_id'

    class client_context(object):
        custom = {'my_custom': 'my_custom_value'}
        env = {'my_env': 'my_env_value'}

        class client(object):
            installation_id = 'my_installation_id'
            app_title = 'my_app_title'
            app_version_name = 'my_app_version_name'
            app_version_code = 'app_version_code'
            app_package_name = 'app_package_name'
