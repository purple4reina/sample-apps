import * as apigateway from 'aws-cdk-lib/aws-apigateway';
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

    // Get default VPC
    const vpc = ec2.Vpc.fromLookup(this, 'ImportVPC', { isDefault: true });

    // Create Security Group for ALB
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc,
      allowAllOutbound: true,
      description: 'Security group for ALB',
    });

    // Create Application Load Balancer (ALB)
    const loadBalancer = new elbv2.ApplicationLoadBalancer(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppALB`, {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
    });

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

    // Create a Listener on the ALB
    const listener = loadBalancer.addListener(`${RESOURCE_ID_PREFIX_CAMEL_CASE}-AlbListener`, {
      port: 80,
      open: true,
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

    // Create API Gateway
    const emptyIntegration = new apigateway.Integration({
      type: apigateway.IntegrationType.HTTP_PROXY,
      integrationHttpMethod: 'ANY',
      options: { connectionType: apigateway.ConnectionType.INTERNET },
      uri: `http://${loadBalancer.loadBalancerDnsName}/`,
    });

    const ddIntegration = new apigateway.Integration({
      type: apigateway.IntegrationType.HTTP_PROXY,
      integrationHttpMethod: 'ANY',
      options: {
        connectionType: apigateway.ConnectionType.INTERNET,
        requestParameters: DatadogAPIGatewayRequestParameters,
      },
      uri: `http://${loadBalancer.loadBalancerDnsName}`,
    });

    const api = new apigateway.RestApi(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-APIGateway`, {
      restApiName: `${RESOURCE_ID_PREFIX_DASH}-api-gateway`,
      description: 'API Gateway for forwarding requests to ALB',
      deployOptions: { stageName: 'prod' },
      defaultIntegration: emptyIntegration,
      parameters: DatadogAPIGatewayRequestParameters,
    });

    api.root.addMethod('ANY');
    const books = api.root.addResource('books');
    books.addMethod('ANY');
    const book = books.addResource('{id}');
    book.addMethod('ANY');
  }
}

