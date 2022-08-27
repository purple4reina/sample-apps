import boto3
import cherrypy
import moto
import os
import uuid

TEST_BUCKET = 'python-agent-test-%s' % uuid.uuid4()

@moto.mock_s3
def client_init():
    aws_access_key_id = os.environ.get(
        'AWS_ACCESS_KEY_ID', 'AAAAAAAAAAAACCESSKEY')
    aws_secret_access_key = os.environ.get(
        'AWS_SECRET_ACCESS_KEY', 'AAAAAASECRETKEY')

    client = boto3.client(
        's3', aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    return client

client = client_init()

class HelloWorld6(object):

    @moto.mock_s3
    def index(self):
        client.create_bucket(Bucket=TEST_BUCKET)
        with open('app.py', 'rb') as data:
            client.upload_fileobj(data, TEST_BUCKET, 'mykey')
        return '*'

    def bototest(self):
        return self.index()

    index.exposed = True
    bototest.exposed = True

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld6())
