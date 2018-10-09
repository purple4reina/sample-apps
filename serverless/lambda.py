import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

from context import Context
import events


def get_arns(event):
    if not hasattr(event, 'get'):
        return None

    records = event.get('Records')
    if records:
        arns = []
        for record in records:

            # S3
            s3 = record.get('s3')
            if s3:
                bucket = s3.get('bucket')
                if bucket:
                    arn = bucket.get('arn')
                    if arn:
                        arns.append(arn)

            # Kinesis, DynamoDB
            arn = record.get('eventSourceARN')
            if arn:
                arns.append(arn)

        return arns

    # Cloudwatch
    resources = event.get('resources')
    if resources:
        return resources

    # API Gateway Authorizer
    method_arn = event.get('methodArn')
    if method_arn:
        return [method_arn]

    # Kinesis Firehose
    deliveryStreamArn = event.get('deliveryStreamArn')
    if deliveryStreamArn:
        return [deliveryStreamArn]

    # Cloudwatch logs, Kinesis firehose, API Gateway
    return []


def get_region(event):
    if not hasattr(event, 'get'):
        return None

    records = event.get('Records')
    if records:
        regions = []
        for record in records:

            # S3, Kinesis, DynamoDB
            aws_region = record.get('awsRegion')
            if aws_region:
                regions.append(aws_region)

        return regions

    # Cloudwatch, Kinesis firehose
    region = event.get('region')
    if region:
        return [region]

    # Cloudwatch logs, API Gateway, API Gateway Authorizer
    return []


@newrelic.agent.lambda_handler()
def handler(event, context):
    return {}


if __name__ == '__main__':
    handler({}, Context())
