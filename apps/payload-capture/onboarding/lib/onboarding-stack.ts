import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';
import { DatadogLambda, DatadogDefaultLayerVersions } from 'datadog-cdk-constructs-v2';

// Fixed name so the traffic scripts (scripts/enable-traffic.sh,
// scripts/disable-traffic.sh) can find the rule without reading stack outputs.
const PRODUCER_SCHEDULE_RULE_NAME = 'rey-storefront-producer-schedule';

export class ReyOnboardingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /*****************
     * Queues        *
     *****************/

    const deadLetterQueue = new sqs.Queue(this, 'StorefrontOrdersDLQ', {
      queueName: 'rey-storefront-orders-dlq',
      retentionPeriod: cdk.Duration.days(14),
    });

    const queue = new sqs.Queue(this, 'StorefrontOrdersQueue', {
      queueName: 'rey-storefront-orders-queue',
      visibilityTimeout: cdk.Duration.seconds(180),
      deadLetterQueue: { queue: deadLetterQueue, maxReceiveCount: 3 },
    });

    /*****************
     * Lambdas       *
     *****************/

    const producer = new lambda.Function(this, 'StorefrontProducer', {
      functionName: 'rey-storefront-producer',
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('src/producer'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        QUEUE_URL: queue.queueUrl,
        BATCH_SIZE: '30',
      },
    });
    queue.grantSendMessages(producer);

    const processor = new lambda.Function(this, 'StorefrontProcessor', {
      functionName: 'rey-storefront-processor',
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('src/processor'),
      timeout: cdk.Duration.seconds(30),
    });
    // One message per invocation so each order is its own captured payload.
    processor.addEventSource(new SqsEventSource(queue, { batchSize: 1 }));

    /**********************************
     * Continuous synthetic traffic   *
     * Off by default — scripts/enable-traffic.sh / disable-traffic.sh flip *
     * this rule without a redeploy. Redeploying resets it back to disabled.*
     **********************************/

    new events.Rule(this, 'ProducerSchedule', {
      ruleName: PRODUCER_SCHEDULE_RULE_NAME,
      schedule: events.Schedule.rate(cdk.Duration.minutes(1)),
      targets: [new targets.LambdaFunction(producer)],
      enabled: false,
    });

    /*****************************************************
     * Datadog instrumentation (payload capture ENABLED) *
     *****************************************************/

    const ddProducer = new DatadogLambda(this, 'DatadogProducer', {
      nodeLayerVersion: DatadogDefaultLayerVersions.NODE,
      extensionLayerVersion: DatadogDefaultLayerVersions.EXTENSION,
      apiKey: process.env.DD_API_KEY,
      site: process.env.DD_SITE || 'datadoghq.com',
      captureLambdaPayload: true,
      sourceCodeIntegration: false,
      service: 'rey-storefront-producer',
      env: 'rey',
    });
    ddProducer.addLambdaFunctions([producer]);

    const ddProcessor = new DatadogLambda(this, 'DatadogProcessor', {
      nodeLayerVersion: DatadogDefaultLayerVersions.NODE,
      extensionLayerVersion: DatadogDefaultLayerVersions.EXTENSION,
      apiKey: process.env.DD_API_KEY,
      site: process.env.DD_SITE || 'datadoghq.com',
      captureLambdaPayload: true,
      sourceCodeIntegration: false,
      service: 'rey-storefront-processor',
      env: 'rey',
    });
    ddProcessor.addLambdaFunctions([processor]);

    /*****************
     * Outputs       *
     *****************/

    new cdk.CfnOutput(this, 'QueueUrl', { value: queue.queueUrl });
    new cdk.CfnOutput(this, 'DeadLetterQueueUrl', { value: deadLetterQueue.queueUrl });
    new cdk.CfnOutput(this, 'ProducerFunction', { value: producer.functionName });
    new cdk.CfnOutput(this, 'ProcessorFunction', { value: processor.functionName });
    new cdk.CfnOutput(this, 'ProducerScheduleRule', { value: PRODUCER_SCHEDULE_RULE_NAME });
  }
}
