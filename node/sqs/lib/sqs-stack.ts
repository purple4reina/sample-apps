import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';

export class SqsStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const queue = new sqs.Queue(this, 'ReySqsQueue', {
      visibilityTimeout: Duration.seconds(300)
    });

    // client
    const client = new lambda.Function(this, 'ReySQSClient', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handle',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        SQS_QUEUE_URL: queue.queueUrl
      }
    });
    const functionUrl = client.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    });
    client.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['sqs:SendMessage'],
        resources: [queue.queueArn],
      })
    );

    // server
    const server = new lambda.Function(this, 'ReySQSServer', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handle',
      code: lambda.Code.fromAsset('lambda'),
    });
    server.addEventSource(new sources.SqsEventSource(queue, { batchSize: 1 }));

    // output the queue url and lambda function url
    new cdk.CfnOutput(this, 'QueueUrl', {
      value: queue.queueUrl,
      description: 'The URL of the SQS queue',
    });
    new cdk.CfnOutput(this, 'ClientFunctionUrl', {
      value: functionUrl.url,
      description: 'The URL of the SQS client function',
    });
  }
}
