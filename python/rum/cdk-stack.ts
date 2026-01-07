#!/usr/bin/env node
import 'source-map-support/register';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as elbv2_targets from 'aws-cdk-lib/aws-elasticloadbalancingv2-targets';
import { Construct } from 'constructs';
import { DatadogLambda } from 'datadog-cdk-constructs-v2';

export class ReyPythonAuthorizerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /**************************
     * Create Lambda Function *
     * ************************/

    const appLambda = new cdk.aws_lambda.Function(this, `Rey-ApplicationFunction`, {
      runtime: cdk.aws_lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: cdk.aws_lambda.Code.fromAsset(__dirname, {
        exclude: ['*.ts', '*.js', '*.json', 'cdk.out', 'node_modules', 'README.md'],
      }),
    });

    // function url
    const functionUrl = appLambda.addFunctionUrl({
      authType: cdk.aws_lambda.FunctionUrlAuthType.NONE,
    });

    /****************************************
     * Lambda Authorizer For API Gateway v1 *
     * **************************************/

    const authLambda = new cdk.aws_lambda.Function(this, `Rey-AuthorizerFunction`, {
      runtime: cdk.aws_lambda.Runtime.PYTHON_3_12,
      handler: 'handler.authorizer',
      code: cdk.aws_lambda.Code.fromAsset(__dirname, {
        exclude: ['*.ts', '*.js', '*.json', 'cdk.out', 'node_modules', 'README.md'],
      }),
    });

    // either TokenAuthorizer or RequestAuthorizer
    // for payload differences, see:
    // https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-input.html
    const tokenAuthorizer = new apigw.TokenAuthorizer(this, 'ReyTokenAuthorizer', {
      handler: authLambda,
      resultsCacheTtl: cdk.Duration.seconds(300),
    });
    const requestAuthorizer = new apigw.RequestAuthorizer(this, 'ReyRequestAuthorizer', {
      handler: authLambda,
      identitySources: [apigw.IdentitySource.header('Authorization')],
      resultsCacheTtl: cdk.Duration.seconds(300),
    });

    /***************************
     * Datadog Instrumentation *
     ***************************/

    const datadogLambda = new DatadogLambda(this, 'datadogLambda', {
      pythonLayerVersion: 120,
      extensionLayerVersion: 90,
      apiKey: process.env.DD_API_KEY || '',
      captureLambdaPayload: true,
      service: 'rey-python-authorizer',
      logLevel: 'debug',
    });
    datadogLambda.addLambdaFunctions([appLambda, authLambda]);

    /*************************
     * Create API Gateway v1 *
     *************************/

    const restApi = new apigw.RestApi(this, `Rey-APIGateway`, {
      restApiName: `Rey-api-gateway-v1`,
      description: 'API Gateway for forwarding requests to ALB',
      deployOptions: { stageName: 'prod' },
    });

    const tokenResource = restApi.root.addResource('token');
    tokenResource.addMethod('ANY', new apigw.LambdaIntegration(appLambda), { authorizer: tokenAuthorizer });

    const requestResource = restApi.root.addResource('request');
    requestResource.addMethod('ANY', new apigw.LambdaIntegration(appLambda), { authorizer: requestAuthorizer });

    /*****************
     * Final Outputs *
     *****************/

    // Output the API Gateway URL and ALB DNS for testing
    new cdk.CfnOutput(this, 'ApplicationLambdaName', { value: appLambda.functionName });
    new cdk.CfnOutput(this, 'AuthorizerLambdaName', { value: authLambda.functionName });
    new cdk.CfnOutput(this, 'FunctionUrl', { value: functionUrl.url });
  }
}

const app = new cdk.App();
new ReyPythonAuthorizerStack(app, 'ReyPythonAuthorizerStack', {
  env: {
    account: '425362996713',
    region: 'sa-east-1',
  },
}); 
