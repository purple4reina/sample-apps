#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class DurableFunctionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const durableFunction = new lambda.Function(this, 'ReyDurableFunction', {
      runtime: lambda.Runtime.PYTHON_3_14,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('.', { exclude: ['**/!(handler.py)', '.*'] }),
      functionName: 'rey-durable-function',
      durableConfig: {
        executionTimeout: cdk.Duration.hours(1),
        retentionPeriod: cdk.Duration.days(7),
      },
    });
  }
}

const app = new cdk.App();
new DurableFunctionStack(app, 'ReyDurableFunctionStack', {
});
