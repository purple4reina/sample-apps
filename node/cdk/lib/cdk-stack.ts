import { Construct } from 'constructs';
import { DatadogLambda } from "datadog-cdk-constructs-v2";
import { Stack, StackProps } from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';

export class CdkStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lambdaFunc = new lambda.Function(this, 'rey-cdk-service', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: "handler.handler",
      code: lambda.Code.fromAsset("src"),
    });

    const api = new apigateway.LambdaRestApi(this, 'ReyEndpoint', {
      handler: lambdaFunc,
    });
    lambdaFunc.grantInvoke(new iam.ServicePrincipal('apigateway.amazonaws.com'));

    const datadog = new DatadogLambda(this, 'DatadogLambda', {
      nodeLayerVersion: 125,
      extensionLayerVersion: 78,
      apiKey: process.env.DD_API_KEY,
      env: "rey",
      service: "rey-cdk-service",
    });
    datadog.addLambdaFunctions([lambdaFunc]);
  }
}
