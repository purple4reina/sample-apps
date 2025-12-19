#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class DurableFunctionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const durableFunction = new lambda.Function(this, 'ReyDurableFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('.', { exclude: ['**/!(handler.py)', '.*'] }),
      functionName: 'rey-durable-function',
      durableConfig: {
        executionTimeout: cdk.Duration.hours(1),
        retentionPeriod: cdk.Duration.days(7),
      },
    });

    const durableUrl = durableFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    });

    durableFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'lambda:CheckpointDurableExecutions',
        'lambda:GetDurableExecutionState',
      ],
      resources: [durableFunction.functionArn],
    }));

    new cdk.CfnOutput(this, 'FunctionAliasArn', { value: durableUrl.url });
  }
}

const app = new cdk.App();
new DurableFunctionStack(app, 'ReyDurableFunctionStack', {
});
