#!/usr/bin/env node
import 'source-map-support/register';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as elbv2_targets from 'aws-cdk-lib/aws-elasticloadbalancingv2-targets';
import { Construct } from 'constructs';
import { DatadogLambda } from "datadog-cdk-constructs-v2";

export class ReyRumLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /**************************
     * Create Lambda Function *
     * ************************/

    const appLambda = new cdk.aws_lambda.Function(this, `Rey-HeaderFunction`, {
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
    new cdk.CfnOutput(this, 'FunctionUrl', { value: functionUrl.url });

    const datadogLambda = new DatadogLambda(this, "datadogLambda", {
      pythonLayerVersion: 120,
      extensionLayerVersion: 90,
      apiKey: process.env.DD_API_KEY || '',
    });
    datadogLambda.addLambdaFunctions([appLambda]);

    /************************
     * Create Load Balancer *
     ************************/

    // Get default VPC
    const vpc = ec2.Vpc.fromLookup(this, 'ImportVPC', { isDefault: true });

    // Create Application Load Balancer (ALB)
    const loadBalancer = new elbv2.ApplicationLoadBalancer(this, `Rey-AppALB`, {
      vpc,
      internetFacing: true,
    });

    // Create a Listener on the ALB
    const listener = loadBalancer.addListener('Rey-AlbListener', {
      port: 80,
      open: true,
      protocol: elbv2.ApplicationProtocol.HTTP,
    });

    // Attach Lambda Function to the ALB Target Group
    listener.addTargets('ReyLambdaGroup', {
      targets: [new elbv2_targets.LambdaTarget(appLambda)],
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(60),
      },
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
    datadogLambda.addLambdaFunctions([authLambda]);

    const authorizer = new apigw.RequestAuthorizer(this, 'ReyRequestAuthorizer', {
      handler: authLambda,
      identitySources: [apigw.IdentitySource.header('Authorization')],
      resultsCacheTtl: cdk.Duration.seconds(300),
    });

    /*************************
     * Create API Gateway v1 *
     *************************/

    const integrationV1 = new apigw.Integration({
      type: apigw.IntegrationType.HTTP_PROXY,
      integrationHttpMethod: 'ANY',
      options: { connectionType: apigw.ConnectionType.INTERNET },
      uri: `http://${loadBalancer.loadBalancerDnsName}`,
    });

    const restApi = new apigw.RestApi(this, `Rey-APIGateway`, {
      restApiName: `Rey-api-gateway-v1`,
      description: 'API Gateway for forwarding requests to ALB',
      deployOptions: { stageName: 'prod' },
      defaultIntegration: integrationV1,
    });

    restApi.root.addMethod('ANY', new apigw.LambdaIntegration(authLambda), {
      authorizer,
      authorizationType: apigw.AuthorizationType.CUSTOM, // Required for V1 custom authorizers
    });

    /*****************
     * Final Outputs *
     *****************/

    // Output the API Gateway URL and ALB DNS for testing
    new cdk.CfnOutput(this, 'ApiGatewayUrl', {
      value: restApi.url,
      description: 'API Gateway URL',
    });
    new cdk.CfnOutput(this, 'AlbDnsName', {
      value: loadBalancer.loadBalancerDnsName,
      description: 'ALB DNS Name',
    });
  }
}

const app = new cdk.App();
new ReyRumLambdaStack(app, 'ReyRumLambdaStack', {
  env: {
    account: '425362996713',
    region: 'sa-east-1',
  },
}); 
