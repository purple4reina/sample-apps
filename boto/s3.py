import botocore
import moto
import uuid

from newrelic.common.object_wrapper import transient_function_wrapper

AWS_ACCESS_KEY_ID = 'AAAAAAAAAAAACCESSKEY'
AWS_SECRET_ACCESS_KEY = 'AAAAAASECRETKEY'
AWS_REGION = 'us-east-1'
TEST_BUCKET = 'python-agent-test-%s' % uuid.uuid4()
REQUEST_ID = str(uuid.uuid4())


@transient_function_wrapper('moto.core.models', 'BotocoreStubber.__call__')
def add_request_id_to_aws_response(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    if response is None:
        return response
    if 'x-amz-request-id' not in response.headers:
        response.headers['x-amz-request-id'] = REQUEST_ID
    return response


@add_request_id_to_aws_response
@moto.mock_s3
def main():
    # Create client
    session = botocore.session.get_session()
    client = session.create_client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Create bucket
    print('----------------------------------------')
    print('CREATE')
    resp = client.create_bucket(Bucket=TEST_BUCKET)
    print('resp: ', resp)

    # Put object
    print('----------------------------------------')
    print('PUT')
    resp = client.put_object(
            Bucket=TEST_BUCKET,
            Key='hello_world',
            Body=b'hello_world_content'
    )
    print('resp: ', resp)

    # List bucket
    print('----------------------------------------')
    print('LIST')
    resp = client.list_objects(Bucket=TEST_BUCKET)
    print('resp: ', resp)
    print('----------------------------------------')


if __name__ == '__main__':
    main()
