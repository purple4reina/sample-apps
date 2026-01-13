#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { DatadogLambda } from "datadog-cdk-constructs-v2";

export class DurableFunctionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const durableFunction = new lambda.Function(this, 'ReyDurableFunction', {
      runtime: lambda.Runtime.PYTHON_3_14,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('.', { exclude: ['**/!(handler.py)', '.*'] }),
      functionName: 'rey-durable-function',
      durableConfig: {
        executionTimeout: cdk.Duration.seconds(120),
        retentionPeriod: cdk.Duration.days(3),
      },
    });

    const datadogLambda = new DatadogLambda(this, "datadogLambda", {
      pythonLayerVersion: 120,
      extensionLayerVersion: 91,
      apiKey: process.env.DD_API_KEY,
      captureLambdaPayload: true,
      logLevel: 'debug',
    });
    datadogLambda.addLambdaFunctions([durableFunction]);

    new cdk.CfnOutput(this, 'FunctionArn', { value: durableFunction.functionArn });
  }
}

const app = new cdk.App();
new DurableFunctionStack(app, 'ReyDurableFunctionStack', {});
