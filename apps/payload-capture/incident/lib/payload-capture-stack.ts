import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';
import { DatadogLambda } from 'datadog-cdk-constructs-v2';

// Fixed name so the toggle scripts (scripts/set-generation.sh) can find the
// parameter without reading stack outputs.
const FORMAT_PARAM_NAME = '/rey/payload-capture/format-generation';

const NODE_LAYER_VERSION = 125;
const EXTENSION_LAYER_VERSION = 91;

export class ReyPayloadCaptureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /*****************************************************************
     * Upstream format toggle                                       *
     * A data-only switch read by the producer at runtime. Flipping *
     * it never touches the processor's code or configuration.      *
     *****************************************************************/

    const formatParam = new ssm.StringParameter(this, 'FormatGenerationParam', {
      parameterName: FORMAT_PARAM_NAME,
      stringValue: 'stable',
      description: 'Wire format the settlement producer emits (stable | next | scheme-case | datetime | counterparty).',
    });

    /*****************
     * Queues        *
     *****************/

    const deadLetterQueue = new sqs.Queue(this, 'SettlementDLQ', {
      queueName: 'rey-settlement-dlq',
      retentionPeriod: cdk.Duration.days(14),
    });

    const queue = new sqs.Queue(this, 'SettlementQueue', {
      queueName: 'rey-settlement-queue',
      visibilityTimeout: cdk.Duration.seconds(180),
      deadLetterQueue: { queue: deadLetterQueue, maxReceiveCount: 3 },
    });

    /*****************
     * Lambdas       *
     *****************/

    const producer = new lambda.Function(this, 'SettlementProducer', {
      functionName: 'rey-settlement-producer',
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('src/producer'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        QUEUE_URL: queue.queueUrl,
        FORMAT_PARAM_NAME,
        BATCH_SIZE: '60',
        DRIFT_RATIO: '0.4',
      },
    });
    queue.grantSendMessages(producer);
    formatParam.grantRead(producer);

    const processor = new lambda.Function(this, 'SettlementProcessor', {
      functionName: 'rey-settlement-processor',
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('src/processor'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        PERMITTED_WINDOW_DAYS: '5',
      },
    });
    // One message per invocation so each failed settlement is one errored
    // invocation (and one captured payload) rather than a partial batch.
    processor.addEventSource(new SqsEventSource(queue, { batchSize: 1 }));

    /**********************************
     * Continuous synthetic traffic   *
     **********************************/

    new events.Rule(this, 'ProducerSchedule', {
      schedule: events.Schedule.rate(cdk.Duration.minutes(1)),
      targets: [new targets.LambdaFunction(producer)],
    });

    /*****************************************************
     * Datadog instrumentation (payload capture ENABLED) *
     *****************************************************/

    const ddProducer = new DatadogLambda(this, 'DatadogProducer', {
      nodeLayerVersion: NODE_LAYER_VERSION,
      extensionLayerVersion: EXTENSION_LAYER_VERSION,
      apiKey: process.env.DD_API_KEY,
      site: process.env.DD_SITE || 'datadoghq.com',
      captureLambdaPayload: true,
      sourceCodeIntegration: false,
      service: 'rey-settlement-producer',
      env: 'rey',
    });
    ddProducer.addLambdaFunctions([producer]);

    const ddProcessor = new DatadogLambda(this, 'DatadogProcessor', {
      nodeLayerVersion: NODE_LAYER_VERSION,
      extensionLayerVersion: EXTENSION_LAYER_VERSION,
      apiKey: process.env.DD_API_KEY,
      site: process.env.DD_SITE || 'datadoghq.com',
      captureLambdaPayload: true,
      sourceCodeIntegration: false,
      service: 'rey-settlement-processor',
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
    new cdk.CfnOutput(this, 'FormatParam', { value: FORMAT_PARAM_NAME });
  }
}
