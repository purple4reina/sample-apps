import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as apigatewayv2_integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import { Construct } from 'constructs';

import { DatadogECSFargate, DatadogAPIGatewayRequestParameters } from "datadog-cdk-constructs-v2";

const DD_API_KEY = process.env.DD_API_KEY || '';
const APP_LANGUAGE = 'js'; // Must match the directory that contains the Dockerfile.
const RESOURCE_ID_PREFIX_CAMEL_CASE = 'ApigwFargateDemo';
const RESOURCE_ID_PREFIX_DASH = 'apigw-fargate-demo';

export class EcsFargateStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /**********************************
     * Create Fargate task definition *
     **********************************/

    // Create Datadog ECS Fargate
    const ecsDatadog = new DatadogECSFargate({
      apiKey: DD_API_KEY,
      env: 'rey',
      apm: {
        isEnabled: true,
        traceInferredProxyServices: true,
      },
    });

    // Create Task Definition
    const taskDefinition = ecsDatadog.fargateTaskDefinition(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-AppTask`, {
      memoryLimitMiB: 512,
      cpu: 256,
    });

    // Add service container to task definition.
    const serviceContainer = taskDefinition.addContainer(`${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-AppContainer`, {
      image: ecs.ContainerImage.fromAsset(`../${APP_LANGUAGE}`, {
        buildArgs: { PLATFORM: 'linux/amd64' },
        platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: `${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-App`,
      }),
      portMappings: [{
        containerPort: 3000,
        hostPort: 3000,
        protocol: ecs.Protocol.TCP
      }],
    });

    /**************************
     * Create Fargate service *
     **************************/

    // Get default VPC
    const vpc = ec2.Vpc.fromLookup(this, 'ImportVPC', { isDefault: true });

    // Create Security Group for Fargate Service
    const serviceSecurityGroup = new ec2.SecurityGroup(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppSecurityGroup`, {
      vpc,
      allowAllOutbound: true,
      description: `${RESOURCE_ID_PREFIX_CAMEL_CASE} App Security Group`,
    });
    serviceSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(3000), 'Allow App traffic');

    // Create Fargate Service
    const cluster = new ecs.Cluster(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppCluster`, {
      vpc,
      clusterName: `${RESOURCE_ID_PREFIX_DASH}-app-cluster`,
    });
    const service = new ecs.FargateService(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppService`, {
      cluster,
      taskDefinition,
      desiredCount: 2,
      assignPublicIp: true,
      securityGroups: [serviceSecurityGroup],
    });

    /************************
     * Create Load Balancer *
     ************************/

    // Create Application Load Balancer (ALB)
    const loadBalancer = new elbv2.ApplicationLoadBalancer(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppALB`, {
      vpc,
      internetFacing: true,
    });

    // Create a Listener on the ALB
    const listener = loadBalancer.addListener(`${RESOURCE_ID_PREFIX_CAMEL_CASE}-AlbListener`, {
      port: 80,
      open: true,
      protocol: elbv2.ApplicationProtocol.HTTP,
    });

    // Attach Fargate Service to the ALB Target Group
    listener.addTargets('FargateTargetGroup', {
      port: 3000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targets: [service.loadBalancerTarget({
        containerName: serviceContainer.containerName,
        containerPort: 3000,
      })],
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(30),
      },
    });

    /*************************
     * Create API Gateway v1 *
     *************************/

    const integrationV1 = new apigateway.Integration({
      type: apigateway.IntegrationType.HTTP_PROXY,
      integrationHttpMethod: 'ANY',
      options: {
        connectionType: apigateway.ConnectionType.INTERNET,
        requestParameters: DatadogAPIGatewayRequestParameters,
      },
      uri: `http://${loadBalancer.loadBalancerDnsName}`,
    });

    const restApi = new apigateway.RestApi(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-APIGateway`, {
      restApiName: `${RESOURCE_ID_PREFIX_DASH}-api-gateway-v1`,
      description: 'API Gateway for forwarding requests to ALB',
      deployOptions: { stageName: 'prod' },
      defaultIntegration: integrationV1,
      parameters: DatadogAPIGatewayRequestParameters,
    });

    restApi.root.addMethod('ANY');
    const magazines = restApi.root.addResource('magazines');
    magazines.addMethod('ANY');
    const magazine = magazines.addResource('{id}');
    magazine.addMethod('ANY');

    /*************************
     * Create API Gateway v2 *
     *************************/

    const httpApi = new apigatewayv2.HttpApi(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-APIGatewayV2`, {
      apiName: `${RESOURCE_ID_PREFIX_DASH}-api-gateway-v2`,
    });

    // Create HTTP integration with ALB
    const albIntegration = new apigatewayv2_integrations.HttpUrlIntegration(
      'HttpUrlIntegration',
      // XXX: I don't understand why this doesn't work
      //`http://${loadBalancer.loadBalancerDnsName}`,
      'http://apigwF-Apigw-McMoYJW8TrKG-306448024.us-west-2.elb.amazonaws.com',
      {
        parameterMapping: new apigatewayv2.ParameterMapping()
          .appendHeader('x-dd-proxy', apigatewayv2.MappingValue.custom('aws-apigateway'))
          .appendHeader('x-dd-proxy-request-time-ms', apigatewayv2.MappingValue.custom('${context.requestTimeEpoch}000'))
          .appendHeader('x-dd-proxy-domain-name', apigatewayv2.MappingValue.custom('$context.domainName'))
          .appendHeader('x-dd-proxy-httpmethod', apigatewayv2.MappingValue.custom('$context.httpMethod'))
          .appendHeader('x-dd-proxy-path', apigatewayv2.MappingValue.custom('$context.path'))
          .appendHeader('x-dd-proxy-stage', apigatewayv2.MappingValue.custom('$context.stage')),
      },
    );

    // Add routes with the integration
    httpApi.addRoutes({
      path: '/{proxy+}',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: albIntegration,
    });
    httpApi.addRoutes({
      path: '/books',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: albIntegration,
    });
    httpApi.addRoutes({
      path: '/books/{id}',
      methods: [apigatewayv2.HttpMethod.ANY],
      integration: albIntegration,
    });

    /*****************
     * Final Outputs *
     *****************/

    // Output the API Gateway URL and ALB DNS for testing
    new cdk.CfnOutput(this, 'ApiGatewayV2Url', {
      value: httpApi.url!,
      description: 'API Gateway URL',
    });
    new cdk.CfnOutput(this, 'AlbDnsName', {
      value: loadBalancer.loadBalancerDnsName,
      description: 'ALB DNS Name',
    });
  }
}
