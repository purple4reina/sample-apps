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
      environment: {
        "DD_ENV": "rey",
        "DD_SERVICE": "rey-cdk-service",
        //"DD_TRACE_INFERRED_PROXY_SERVICES_ENABLED": "true",
        "DD_TRACE_OTEL_ENABLED": "false",
        "DD_PROFILING_ENABLED": "false",
        "DD_SERVERLESS_APPSEC_ENABLED": "false",
      },
    });

    const api = new apigateway.LambdaRestApi(this, 'ReyEndpoint', {
      handler: lambdaFunc,
    });
    lambdaFunc.grantInvoke(new iam.ServicePrincipal('apigateway.amazonaws.com'));

    const datadog = new DatadogLambda(this, 'DatadogLambda', {
      nodeLayerVersion: 125, // upgraded from 115 to 125
      extensionLayerVersion: 78, // upgraded from 63 to 78
      apiKey: process.env.DD_API_KEY,
    });
    datadog.addLambdaFunctions([lambdaFunc]);
  }
}
