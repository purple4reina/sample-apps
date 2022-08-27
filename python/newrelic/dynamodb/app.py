import newrelic.agent

newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import botocore.session
import moto
import uuid

AWS_ACCESS_KEY_ID = 'AAAAAAAAAAAACCESSKEY'
AWS_SECRET_ACCESS_KEY = 'AAAAAASECRETKEY'
AWS_REGION = 'us-east-1'
TEST_TABLE = 'python-agent-test-%s' % uuid.uuid4()


@newrelic.agent.background_task()
@moto.mock_dynamodb2
def main():
    session = botocore.session.get_session()
    client = session.create_client(
            'dynamodb',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Create table
    resp = client.create_table(
            TableName=TEST_TABLE,
            AttributeDefinitions=[
                    {'AttributeName': 'Id', 'AttributeType': 'N'},
                    {'AttributeName': 'Foo', 'AttributeType': 'S'},
            ],
            KeySchema=[
                    {'AttributeName': 'Id', 'KeyType': 'HASH'},
                    {'AttributeName': 'Foo', 'KeyType': 'RANGE'},
            ],
            ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5,
            },
    )
    print('resp: ', resp)


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
