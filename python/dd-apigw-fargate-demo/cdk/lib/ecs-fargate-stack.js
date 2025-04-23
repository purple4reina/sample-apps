"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EcsFargateStack = void 0;
const apigateway = require("aws-cdk-lib/aws-apigateway");
const cdk = require("aws-cdk-lib");
const ec2 = require("aws-cdk-lib/aws-ec2");
const ecs = require("aws-cdk-lib/aws-ecs");
const elbv2 = require("aws-cdk-lib/aws-elasticloadbalancingv2");
// TODO: Change this to your IP address but leave `/32` at the end
// Find your IP at https://checkip.amazonaws.com)
// const MY_IP_ADDRESS = '0.0.0.0/32';
/*
Best option is to find the albSecurityGroup in AWS Console
(securityGroupId outputted in this script) and manually add a
security rule to open up this ALB to traffic from any IPv4.

Alternatively, grab API Gateway IPs for your region from:
https://ip-ranges.amazonaws.com/ip-ranges.json
Cmd + F for your region and copy-paste all API Gateway IPs.
*/
const DD_API_KEY = process.env.DD_API_KEY || '';
const APP_LANGUAGE = 'js'; // Must match the directory that contains the Dockerfile. 
const RESOURCE_ID_PREFIX_CAMEL_CASE = 'ApigwFargateDemo';
const RESOURCE_ID_PREFIX_DASH = 'apigw-fargate-demo';
class EcsFargateStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        // Get default VPC
        const vpc = ec2.Vpc.fromLookup(this, 'ImportVPC', { isDefault: true });
        // Create ECS Cluster
        const cluster = new ecs.Cluster(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppCluster`, {
            vpc,
            clusterName: `${RESOURCE_ID_PREFIX_DASH}-app-cluster`,
        });
        // Create Task Definition
        const taskDefinition = new ecs.FargateTaskDefinition(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-AppTask`, {
            memoryLimitMiB: 512,
            cpu: 256,
        });
        // Add service container to task definition.
        const serviceContainer = taskDefinition.addContainer(`${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-AppContainer`, {
            image: ecs.ContainerImage.fromAsset(`../${APP_LANGUAGE}`, {
                buildArgs: {
                    PLATFORM: 'linux/amd64'
                },
                platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64,
            }),
            environment: {
                // Set environment variables on service.
                NODE_ENV: 'production',
                //DD_TRACE_DEBUG: 'true',
                // DD_SERVICE: 'fastapi-app',
                // DD_AGENT_HOST: 'datadog-agent',
                DD_ENV: 'rey',
                DD_LOGS_INJECTION: 'true',
                DD_REMOTE_CONFIGURATION_ENABLED: 'false',
                DD_TRACE_INFERRED_PROXY_SERVICES_ENABLED: 'true'
            },
            logging: ecs.LogDrivers.awsLogs({ streamPrefix: `${RESOURCE_ID_PREFIX_CAMEL_CASE}-${APP_LANGUAGE}-App` }),
            portMappings: [
                {
                    containerPort: 3000,
                    hostPort: 3000,
                    protocol: ecs.Protocol.TCP
                }
            ]
        });
        // Add Datadog agent container to task definition.
        const datadogAgentContainer = taskDefinition.addContainer('datadog-agent', {
            image: ecs.ContainerImage.fromRegistry('public.ecr.aws/datadog/agent:latest'),
            environment: {
                DD_API_KEY: DD_API_KEY,
                DD_APM_ENABLED: 'true',
                ECS_FARGATE: 'true',
                //DD_LOG_LEVEL: 'TRACE'
            },
            logging: new ecs.AwsLogDriver({
                streamPrefix: 'DatadogAgentContainer',
            }),
            memoryLimitMiB: 512,
            cpu: 256,
            portMappings: [
                {
                    containerPort: 8126,
                    hostPort: 8126,
                    protocol: ecs.Protocol.TCP
                }
            ]
        });
        // Create Security Group for ALB
        const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
            vpc,
            allowAllOutbound: true,
            description: 'Security group for ALB',
        });
        // Allow inbound HTTP (port 80) traffic to the ALB
        // Only allow traffic from my IP address because the AWS sandbox removes Security Group Rules that are too public.
        // albSecurityGroup.addIngressRule(ec2.Peer.ipv4(MY_IP_ADDRESS), ec2.Port.tcp(80), 'Allow HTTP traffic');
        // Create Application Load Balancer (ALB)
        const loadBalancer = new elbv2.ApplicationLoadBalancer(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppALB`, {
            vpc,
            internetFacing: true,
            securityGroup: albSecurityGroup, // Attach the ALB security group
        });
        // Create a Listener on the ALB
        const listener = loadBalancer.addListener(`${RESOURCE_ID_PREFIX_CAMEL_CASE}-AlbListener`, {
            port: 80, // HTTP Listener
            open: true,
        });
        // Create Security Group for Fargate Service
        const serviceSecurityGroup = new ec2.SecurityGroup(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppSecurityGroup`, {
            vpc,
            allowAllOutbound: true,
            description: `${RESOURCE_ID_PREFIX_CAMEL_CASE} App Security Group`,
        });
        serviceSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(3000), 'Allow App traffic');
        // Create Fargate Service
        const service = new ecs.FargateService(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-AppService`, {
            cluster,
            taskDefinition,
            desiredCount: 2,
            assignPublicIp: true,
            securityGroups: [serviceSecurityGroup],
        });
        // Attach Fargate Service to the ALB Target Group
        listener.addTargets('FargateTargetGroup', {
            port: 3000, // Forward requests to container
            protocol: elbv2.ApplicationProtocol.HTTP,
            targets: [service],
            healthCheck: {
                path: '/health', // Change this if your health check route is different
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
                requestParameters: {
                    "integration.request.header.x-dd-proxy": "'aws-apigateway'",
                    "integration.request.header.x-dd-proxy-request-time-ms": "context.requestTimeEpoch",
                    "integration.request.header.x-dd-proxy-domain-name": "context.domainName",
                    "integration.request.header.x-dd-apigw-domain-prefix": "context.domainPrefix",
                    "integration.request.header.x-dd-apigw-error-message": "context.error.message",
                    "integration.request.header.x-dd-proxy-httpmethod": "context.httpMethod",
                    "integration.request.header.x-dd-apigw-identity-useragent": "context.identity.userAgent",
                    "integration.request.header.x-dd-proxy-path": "context.path",
                    "integration.request.header.x-dd-apigw-protocol": "context.protocol",
                    "integration.request.header.x-dd-proxy-stage": "context.stage",
                }
            },
            uri: `http://${loadBalancer.loadBalancerDnsName}`,
        });
        const api = new apigateway.RestApi(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-APIGateway`, {
            restApiName: `${RESOURCE_ID_PREFIX_DASH}-api-gateway`,
            description: 'API Gateway for forwarding requests to ALB',
            deployOptions: { stageName: 'prod' },
            defaultIntegration: emptyIntegration,
        });
        api.root.addMethod('ANY', ddIntegration);
        const books = api.root.addResource('books');
        books.addMethod('ANY');
        const book = books.addResource('{id}');
        book.addMethod('ANY');
        // Output the task public IP
        new cdk.CfnOutput(this, `${RESOURCE_ID_PREFIX_CAMEL_CASE}-FargateService`, {
            value: service.serviceName,
            description: 'Name of the Fargate service',
        });
        // Output the ALB DNS Name
        new cdk.CfnOutput(this, 'LoadBalancerDNS', {
            value: loadBalancer.loadBalancerDnsName,
            description: 'Application Load Balancer DNS Name',
        });
        // Output the ALB SecurityGroup
        new cdk.CfnOutput(this, 'AlbSecurityGroupId', {
            value: albSecurityGroup.securityGroupId,
            description: 'Application Load Balancer DNS Name',
        });
        // Output API Gateway URL
        new cdk.CfnOutput(this, 'ApiGatewayURL', {
            value: api.url,
            description: 'API Gateway URL',
        });
    }
}
exports.EcsFargateStack = EcsFargateStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZWNzLWZhcmdhdGUtc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJlY3MtZmFyZ2F0ZS1zdGFjay50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSx5REFBeUQ7QUFDekQsbUNBQW1DO0FBQ25DLDJDQUEyQztBQUMzQywyQ0FBMkM7QUFDM0MsZ0VBQWdFO0FBR2hFLGtFQUFrRTtBQUNsRSxpREFBaUQ7QUFDakQsc0NBQXNDO0FBRXRDOzs7Ozs7OztFQVFFO0FBRUYsTUFBTSxVQUFVLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxVQUFVLElBQUksRUFBRSxDQUFDO0FBQ2hELE1BQU0sWUFBWSxHQUFHLElBQUksQ0FBQyxDQUFDLDBEQUEwRDtBQUNyRixNQUFNLDZCQUE2QixHQUFHLGtCQUFrQixDQUFDO0FBQ3pELE1BQU0sdUJBQXVCLEdBQUcsb0JBQW9CLENBQUM7QUFFckQsTUFBYSxlQUFnQixTQUFRLEdBQUcsQ0FBQyxLQUFLO0lBQzVDLFlBQVksS0FBZ0IsRUFBRSxFQUFVLEVBQUUsS0FBc0I7UUFDOUQsS0FBSyxDQUFDLEtBQUssRUFBRSxFQUFFLEVBQUUsS0FBSyxDQUFDLENBQUM7UUFFeEIsa0JBQWtCO1FBQ2xCLE1BQU0sR0FBRyxHQUFHLEdBQUcsQ0FBQyxHQUFHLENBQUMsVUFBVSxDQUFDLElBQUksRUFBRSxXQUFXLEVBQUMsRUFBQyxTQUFTLEVBQUUsSUFBSSxFQUFDLENBQUMsQ0FBQztRQUVwRSxxQkFBcUI7UUFDckIsTUFBTSxPQUFPLEdBQUcsSUFBSSxHQUFHLENBQUMsT0FBTyxDQUFDLElBQUksRUFBRSxHQUFHLDZCQUE2QixhQUFhLEVBQUU7WUFDbkYsR0FBRztZQUNILFdBQVcsRUFBRSxHQUFHLHVCQUF1QixjQUFjO1NBQ3RELENBQUMsQ0FBQztRQUVILHlCQUF5QjtRQUN6QixNQUFNLGNBQWMsR0FBRyxJQUFJLEdBQUcsQ0FBQyxxQkFBcUIsQ0FBQyxJQUFJLEVBQUUsR0FBRyw2QkFBNkIsSUFBSSxZQUFZ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T0FBTyxDQUFDLENBQUM7UUFDNUMsS0FBSyxDQUFDLFNBQVMsQ0FBQyxLQUFLLENBQUMsQ0FBQztRQUN2QixNQUFNLElBQUksR0FBRyxLQUFLLENBQUMsV0FBVyxDQUFDLE1BQU0sQ0FBQyxDQUFDO1FBQ3ZDLElBQUksQ0FBQyxTQUFTLENBQUMsS0FBSyxDQUFDLENBQUM7UUFFdEIsNEJBQTRCO1FBQzVCLElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsR0FBRyw2QkFBNkIsaUJBQWlCLEVBQUU7WUFDekUsS0FBSyxFQUFFLE9BQU8sQ0FBQyxXQUFXO1lBQzFCLFdBQVcsRUFBRSw2QkFBNkI7U0FDM0MsQ0FBQyxDQUFDO1FBRUgsMEJBQTBCO1FBQzFCLElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsaUJBQWlCLEVBQUU7WUFDekMsS0FBSyxFQUFFLFlBQVksQ0FBQyxtQkFBbUI7WUFDdkMsV0FBVyxFQUFFLG9DQUFvQztTQUNsRCxDQUFDLENBQUM7UUFFSCwrQkFBK0I7UUFDL0IsSUFBSSxHQUFHLENBQUMsU0FBUyxDQUFDLElBQUksRUFBRSxvQkFBb0IsRUFBRTtZQUM1QyxLQUFLLEVBQUUsZ0JBQWdCLENBQUMsZUFBZTtZQUN2QyxXQUFXLEVBQUUsb0NBQW9DO1NBQ2xELENBQUMsQ0FBQztRQUVILHlCQUF5QjtRQUN6QixJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLGVBQWUsRUFBRTtZQUN2QyxLQUFLLEVBQUUsR0FBRyxDQUFDLEdBQUc7WUFDZCxXQUFXLEVBQUUsaUJBQWlCO1NBQy9CLENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQTlMRCwwQ0E4TEMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBhcGlnYXRld2F5IGZyb20gJ2F3cy1jZGstbGliL2F3cy1hcGlnYXRld2F5JztcbmltcG9ydCAqIGFzIGNkayBmcm9tICdhd3MtY2RrLWxpYic7XG5pbXBvcnQgKiBhcyBlYzIgZnJvbSAnYXdzLWNkay1saWIvYXdzLWVjMic7XG5pbXBvcnQgKiBhcyBlY3MgZnJvbSAnYXdzLWNkay1saWIvYXdzLWVjcyc7XG5pbXBvcnQgKiBhcyBlbGJ2MiBmcm9tICdhd3MtY2RrLWxpYi9hd3MtZWxhc3RpY2xvYWRiYWxhbmNpbmd2Mic7XG5pbXBvcnQgeyBDb25zdHJ1Y3QgfSBmcm9tICdjb25zdHJ1Y3RzJztcblxuLy8gVE9ETzogQ2hhbmdlIHRoaXMgdG8geW91ciBJUCBhZGRyZXNzIGJ1dCBsZWF2ZSBgLzMyYCBhdCB0aGUgZW5kXG4vLyBGaW5kIHlvdXIgSVAgYXQgaHR0cHM6Ly9jaGVja2lwLmFtYXpvbmF3cy5jb20pXG4vLyBjb25zdCBNWV9JUF9BRERSRVNTID0gJzAuMC4wLjAvMzInO1xuXG4vKlxuQmVzdCBvcHRpb24gaXMgdG8gZmluZCB0aGUgYWxiU2VjdXJpdHlHcm91cCBpbiBBV1MgQ29uc29sZVxuKHNlY3VyaXR5R3JvdXBJZCBvdXRwdXR0ZWQgaW4gdGhpcyBzY3JpcHQpIGFuZCBtYW51YWxseSBhZGQgYVxuc2VjdXJpdHkgcnVsZSB0byBvcGVuIHVwIHRoaXMgQUxCIHRvIHRyYWZmaWMgZnJvbSBhbnkgSVB2NC4gXG5cbkFsdGVybmF0aXZlbHksIGdyYWIgQVBJIEdhdGV3YXkgSVBzIGZvciB5b3VyIHJlZ2lvbiBmcm9tOlxuaHR0cHM6Ly9pcC1yYW5nZXMuYW1hem9uYXdzLmNvbS9pcC1yYW5nZXMuanNvblxuQ21kICsgRiBmb3IgeW91ciByZWdpb24gYW5kIGNvcHktcGFzdGUgYWxsIEFQSSBHYXRld2F5IElQcy5cbiovXG5cbmNvbnN0IEREX0FQSV9LRVkgPSBwcm9jZXNzLmVudi5ERF9BUElfS0VZIHx8ICcnO1xuY29uc3QgQVBQX0xBTkdVQUdFID0gJ2pzJzsgLy8gTXVzdCBtYXRjaCB0aGUgZGlyZWN0b3J5IHRoYXQgY29udGFpbnMgdGhlIERvY2tlcmZpbGUuIFxuY29uc3QgUkVTT1VSQ0VfSURfUFJFRklYX0NBTUVMX0NBU0UgPSAnQXBpZ3dGYXJnYXRlRGVtbyc7XG5jb25zdCBSRVNPVVJDRV9JRF9QUkVGSVhfREFTSCA9ICdhcGlndy1mYXJnYXRlLWRlbW8nO1xuXG5leHBvcnQgY2xhc3MgRWNzRmFyZ2F0ZVN0YWNrIGV4dGVuZHMgY2RrLlN0YWNrIHtcbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBjZGsuU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgLy8gR2V0IGRlZmF1bHQgVlBDXG4gICAgY29uc3QgdnBjID0gZWMyLlZwYy5mcm9tTG9va3VwKHRoaXMsICdJbXBvcnRWUEMnLHtpc0RlZmF1bHQ6IHRydWV9KTtcblxuICAgIC8vIENyZWF0ZSBFQ1MgQ2x1c3RlclxuICAgIGNvbnN0IGNsdXN0ZXIgPSBuZXcgZWNzLkNsdXN0ZXIodGhpcywgYCR7UkVTT1VSQ0VfSURfUFJFRklYX0NBTUVMX0NBU0V9LUFwcENsdXN0ZXJgLCB7XG4gICAgICB2cGMsXG4gICAgICBjbHVzdGVyTmFtZTogYCR7UkVTT1VSQ0VfSURfUFJFRklYX0RBU0h9LWFwcC1jbHVzdGVyYCxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBUYXNrIERlZmluaXRpb25cbiAgICBjb25zdCB0YXNrRGVmaW5pdGlvbiA9IG5ldyBlY3MuRmFyZ2F0ZVRhc2tEZWZpbml0aW9uKHRoaXMsIGAke1JFU09VUkNFX0lEX1BSRUZJWF9DQU1FTF9DQVNFfS0ke0FQUF9MQU5HVUFHRX0tQXBwVGFza2AsIHtcbiAgICAgIG1lbW9yeUxpbWl0TWlCOiA1MTIsXG4gICAgICBjcHU6IDI1NixcbiAgICB9KTtcblxuICAgIC8vIEFkZCBzZXJ2aWNlIGNvbnRhaW5lciB0byB0YXNrIGRlZmluaXRpb24uXG4gICAgY29uc3Qgc2VydmljZUNvbnRhaW5lciA9IHRhc2tEZWZpbml0aW9uLmFkZENvbnRhaW5lcihgJHtSRVNPVVJDRV9JRF9QUkVGSVhfQ0FNRUxfQ0FTRX0tJHtBUFBfTEFOR1VBR0V9LUFwcENvbnRhaW5lcmAsIHtcbiAgICAgIGltYWdlOiBlY3MuQ29udGFpbmVySW1hZ2UuZnJvbUFzc2V0KGAuLi8ke0FQUF9MQU5HVUFHRX1gLCB7XG4gICAgICAgIGJ1aWxkQXJnczoge1xuICAgICAgICAgICAgUExBVEZPUk06ICdsaW51eC9hbWQ2NCdcbiAgICAgICAgfSxcbiAgICAgICAgcGxhdGZvcm06IGNkay5hd3NfZWNyX2Fzc2V0cy5QbGF0Zm9ybS5MSU5VWF9BTUQ2NCxcbiAgICAgIH0pLFxuICAgICAgZW52aXJvbm1lbnQ6IHtcbiAgICAgICAgLy8gU2V0IGVudmlyb25tZW50IHZhcmlhYmxlcyBvbiBzZXJ2aWNlLlxuICAgICAgICBOT0RFX0VOVjogJ3Byb2R1Y3Rpb24nLFxuICAgICAgICAvL0REX1RSQUNFX0RFQlVHOiAndHJ1ZScsXG4gICAgICAgIC8vIEREX1NFUlZJQ0U6ICdmYXN0YXBpLWFwcCcsXG4gICAgICAgIC8vIEREX0FHRU5UX0hPU1Q6ICdkYXRhZG9nLWFnZW50JyxcbiAgICAgICAgRERfRU5WOiAncmV5JyxcbiAgICAgICAgRERfTE9HU19JTkpFQ1RJT046ICd0cnVlJyxcbiAgICAgICAgRERfUkVNT1RFX0NPTkZJR1VSQVRJT05fRU5BQkxFRDogJ2ZhbHNlJyxcbiAgICAgICAgRERfVFJBQ0VfSU5GRVJSRURfUFJPWFlfU0VSVklDRVNfRU5BQkxFRDogJ3RydWUnXG4gICAgICB9LFxuICAgICAgbG9nZ2luZzogZWNzLkxvZ0RyaXZlcnMuYXdzTG9ncyh7IHN0cmVhbVByZWZpeDogYCR7UkVTT1VSQ0VfSURfUFJFRklYX0NBTUVMX0NBU0V9LSR7QVBQX0xBTkdVQUdFfS1BcHBgIH0pLFxuICAgICAgcG9ydE1hcHBpbmdzOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBjb250YWluZXJQb3J0OiAzMDAwLFxuICAgICAgICAgIGhvc3RQb3J0OiAzMDAwLFxuICAgICAgICAgIHByb3RvY29sOiBlY3MuUHJvdG9jb2wuVENQXG4gICAgICAgIH1cbiAgICAgIF1cbiAgICB9KTtcblxuICAgIC8vIEFkZCBEYXRhZG9nIGFnZW50IGNvbnRhaW5lciB0byB0YXNrIGRlZmluaXRpb24uXG4gICAgY29uc3QgZGF0YWRvZ0FnZW50Q29udGFpbmVyID0gdGFza0RlZmluaXRpb24uYWRkQ29udGFpbmVyKCdkYXRhZG9nLWFnZW50Jywge1xuICAgICAgaW1hZ2U6IGVjcy5Db250YWluZXJJbWFnZS5mcm9tUmVnaXN0cnkoJ3B1YmxpYy5lY3IuYXdzL2RhdGFkb2cvYWdlbnQ6bGF0ZXN0JyksXG4gICAgICBlbnZpcm9ubWVudDoge1xuICAgICAgICBERF9BUElfS0VZOiBERF9BUElfS0VZLFxuICAgICAgICBERF9BUE1fRU5BQkxFRDogJ3RydWUnLFxuICAgICAgICBFQ1NfRkFSR0FURTogJ3RydWUnLFxuICAgICAgICAvL0REX0xPR19MRVZFTDogJ1RSQUNFJ1xuICAgICAgfSxcbiAgICAgIGxvZ2dpbmc6IG5ldyBlY3MuQXdzTG9nRHJpdmVyKHtcbiAgICAgICAgc3RyZWFtUHJlZml4OiAnRGF0YWRvZ0FnZW50Q29udGFpbmVyJyxcbiAgICAgIH0pLFxuICAgICAgbWVtb3J5TGltaXRNaUI6IDUxMixcbiAgICAgIGNwdTogMjU2LFxuICAgICAgcG9ydE1hcHBpbmdzOiBbXG4gICAgICAgIHtcbiAgICAgICAgICAgIGNvbnRhaW5lclBvcnQ6IDgxMjYsXG4gICAgICAgICAgICBob3N0UG9ydDogODEyNixcbiAgICAgICAgICAgIHByb3RvY29sOiBlY3MuUHJvdG9jb2wuVENQXG4gICAgICAgIH1cbiAgICBdXG4gICAgfSk7XG5cbiAgICAvLyBDcmVhdGUgU2VjdXJpdHkgR3JvdXAgZm9yIEFMQlxuICAgIGNvbnN0IGFsYlNlY3VyaXR5R3JvdXAgPSBuZXcgZWMyLlNlY3VyaXR5R3JvdXAodGhpcywgJ0FMQlNlY3VyaXR5R3JvdXAnLCB7XG4gICAgICB2cGMsXG4gICAgICBhbGxvd0FsbE91dGJvdW5kOiB0cnVlLFxuICAgICAgZGVzY3JpcHRpb246ICdTZWN1cml0eSBncm91cCBmb3IgQUxCJyxcbiAgICB9KTtcblxuICAgIC8vIEFsbG93IGluYm91bmQgSFRUUCAocG9ydCA4MCkgdHJhZmZpYyB0byB0aGUgQUxCXG4gICAgLy8gT25seSBhbGxvdyB0cmFmZmljIGZyb20gbXkgSVAgYWRkcmVzcyBiZWNhdXNlIHRoZSBBV1Mgc2FuZGJveCByZW1vdmVzIFNlY3VyaXR5IEdyb3VwIFJ1bGVzIHRoYXQgYXJlIHRvbyBwdWJsaWMuXG4gICAgLy8gYWxiU2VjdXJpdHlHcm91cC5hZGRJbmdyZXNzUnVsZShlYzIuUGVlci5pcHY0KE1ZX0lQX0FERFJFU1MpLCBlYzIuUG9ydC50Y3AoODApLCAnQWxsb3cgSFRUUCB0cmFmZmljJyk7XG5cbiAgICAvLyBDcmVhdGUgQXBwbGljYXRpb24gTG9hZCBCYWxhbmNlciAoQUxCKVxuICAgIGNvbnN0IGxvYWRCYWxhbmNlciA9IG5ldyBlbGJ2Mi5BcHBsaWNhdGlvbkxvYWRCYWxhbmNlcih0aGlzLCBgJHtSRVNPVVJDRV9JRF9QUkVGSVhfQ0FNRUxfQ0FTRX0tQXBwQUxCYCwge1xuICAgICAgdnBjLFxuICAgICAgaW50ZXJuZXRGYWNpbmc6IHRydWUsXG4gICAgICBzZWN1cml0eUdyb3VwOiBhbGJTZWN1cml0eUdyb3VwLCAvLyBBdHRhY2ggdGhlIEFMQiBzZWN1cml0eSBncm91cFxuICAgIH0pO1xuXG4gICAgLy8gQ3JlYXRlIGEgTGlzdGVuZXIgb24gdGhlIEFMQlxuICAgIGNvbnN0IGxpc3RlbmVyID0gbG9hZEJhbGFuY2VyLmFkZExpc3RlbmVyKGAke1JFU09VUkNFX0lEX1BSRUZJWF9DQU1FTF9DQVNFfS1BbGJMaXN0ZW5lcmAsIHtcbiAgICAgIHBvcnQ6IDgwLCAvLyBIVFRQIExpc3RlbmVyXG4gICAgICBvcGVuOiB0cnVlLFxuICAgIH0pO1xuXG4gICAgLy8gQ3JlYXRlIFNlY3VyaXR5IEdyb3VwIGZvciBGYXJnYXRlIFNlcnZpY2VcbiAgICBjb25zdCBzZXJ2aWNlU2VjdXJpdHlHcm91cCA9IG5ldyBlYzIuU2VjdXJpdHlHcm91cCh0aGlzLCBgJHtSRVNPVVJDRV9JRF9QUkVGSVhfQ0FNRUxfQ0FTRX0tQXBwU2VjdXJpdHlHcm91cGAsIHtcbiAgICAgICAgdnBjLFxuICAgICAgICBhbGxvd0FsbE91dGJvdW5kOiB0cnVlLFxuICAgICAgICBkZXNjcmlwdGlvbjogYCR7UkVTT1VSQ0VfSURfUFJFRklYX0NBTUVMX0NBU0V9IEFwcCBTZWN1cml0eSBHcm91cGAsXG4gICAgfSk7IFxuICAgIFxuICAgIHNlcnZpY2VTZWN1cml0eUdyb3VwLmFkZEluZ3Jlc3NSdWxlKGVjMi5QZWVyLmFueUlwdjQoKSwgZWMyLlBvcnQudGNwKDMwMDApLCAnQWxsb3cgQXBwIHRyYWZmaWMnKTtcblxuICAgIC8vIENyZWF0ZSBGYXJnYXRlIFNlcnZpY2VcbiAgICBjb25zdCBzZXJ2aWNlID0gbmV3IGVjcy5GYXJnYXRlU2VydmljZSh0aGlzLCBgJHtSRVNPVVJDRV9JRF9QUkVGSVhfQ0FNRUxfQ0FTRX0tQXBwU2VydmljZWAsIHtcbiAgICAgIGNsdXN0ZXIsXG4gICAgICB0YXNrRGVmaW5pdGlvbixcbiAgICAgIGRlc2lyZWRDb3VudDogMixcbiAgICAgIGFzc2lnblB1YmxpY0lwOiB0cnVlLFxuICAgICAgc2VjdXJpdHlHcm91cHM6IFtzZXJ2aWNlU2VjdXJpdHlHcm91cF0sXG4gICAgfSk7XG5cbiAgICAvLyBBdHRhY2ggRmFyZ2F0ZSBTZXJ2aWNlIHRvIHRoZSBBTEIgVGFyZ2V0IEdyb3VwXG4gICAgbGlzdGVuZXIuYWRkVGFyZ2V0cygnRmFyZ2F0ZVRhcmdldEdyb3VwJywge1xuICAgICAgcG9ydDogMzAwMCwgLy8gRm9yd2FyZCByZXF1ZXN0cyB0byBjb250YWluZXJcbiAgICAgIHByb3RvY29sOiBlbGJ2Mi5BcHBsaWNhdGlvblByb3RvY29sLkhUVFAsXG4gICAgICB0YXJnZXRzOiBbc2VydmljZV0sXG4gICAgICBoZWFsdGhDaGVjazoge1xuICAgICAgICBwYXRoOiAnL2hlYWx0aCcsIC8vIENoYW5nZSB0aGlzIGlmIHlvdXIgaGVhbHRoIGNoZWNrIHJvdXRlIGlzIGRpZmZlcmVudFxuICAgICAgICBpbnRlcnZhbDogY2RrLkR1cmF0aW9uLnNlY29uZHMoMzApLFxuICAgICAgfSxcbiAgICB9KTtcblxuICAgIC8vIENyZWF0ZSBBUEkgR2F0ZXdheVxuICAgIGNvbnN0IGVtcHR5SW50ZWdyYXRpb24gPSBuZXcgYXBpZ2F0ZXdheS5JbnRlZ3JhdGlvbih7XG4gICAgICB0eXBlOiBhcGlnYXRld2F5LkludGVncmF0aW9uVHlwZS5IVFRQX1BST1hZLFxuICAgICAgaW50ZWdyYXRpb25IdHRwTWV0aG9kOiAnQU5ZJyxcbiAgICAgIG9wdGlvbnM6IHsgY29ubmVjdGlvblR5cGU6IGFwaWdhdGV3YXkuQ29ubmVjdGlvblR5cGUuSU5URVJORVQgfSxcbiAgICAgIHVyaTogYGh0dHA6Ly8ke2xvYWRCYWxhbmNlci5sb2FkQmFsYW5jZXJEbnNOYW1lfS9gLFxuICAgIH0pO1xuXG4gICAgY29uc3QgZGRJbnRlZ3JhdGlvbiA9IG5ldyBhcGlnYXRld2F5LkludGVncmF0aW9uKHtcbiAgICAgIHR5cGU6IGFwaWdhdGV3YXkuSW50ZWdyYXRpb25UeXBlLkhUVFBfUFJPWFksXG4gICAgICBpbnRlZ3JhdGlvbkh0dHBNZXRob2Q6ICdBTlknLFxuICAgICAgb3B0aW9uczoge1xuICAgICAgICBjb25uZWN0aW9uVHlwZTogYXBpZ2F0ZXdheS5Db25uZWN0aW9uVHlwZS5JTlRFUk5FVCxcbiAgICAgICAgcmVxdWVzdFBhcmFtZXRlcnM6IHtcbiAgICAgICAgICBcImludGVncmF0aW9uLnJlcXVlc3QuaGVhZGVyLngtZGQtcHJveHlcIjogXCInYXdzLWFwaWdhdGV3YXknXCIsXG4gICAgICAgICAgXCJpbnRlZ3JhdGlvbi5yZXF1ZXN0LmhlYWRlci54LWRkLXByb3h5LXJlcXVlc3QtdGltZS1tc1wiOiBcImNvbnRleHQucmVxdWVzdFRpbWVFcG9jaFwiLFxuICAgICAgICAgIFwiaW50ZWdyYXRpb24ucmVxdWVzdC5oZWFkZXIueC1kZC1wcm94eS1kb21haW4tbmFtZVwiOiBcImNvbnRleHQuZG9tYWluTmFtZVwiLFxuICAgICAgICAgIFwiaW50ZWdyYXRpb24ucmVxdWVzdC5oZWFkZXIueC1kZC1hcGlndy1kb21haW4tcHJlZml4XCI6IFwiY29udGV4dC5kb21haW5QcmVmaXhcIixcbiAgICAgICAgICBcImludGVncmF0aW9uLnJlcXVlc3QuaGVhZGVyLngtZGQtYXBpZ3ctZXJyb3ItbWVzc2FnZVwiOiBcImNvbnRleHQuZXJyb3IubWVzc2FnZVwiLFxuICAgICAgICAgIFwiaW50ZWdyYXRpb24ucmVxdWVzdC5oZWFkZXIueC1kZC1wcm94eS1odHRwbWV0aG9kXCI6IFwiY29udGV4dC5odHRwTWV0aG9kXCIsXG4gICAgICAgICAgXCJpbnRlZ3JhdGlvbi5yZXF1ZXN0LmhlYWRlci54LWRkLWFwaWd3LWlkZW50aXR5LXVzZXJhZ2VudFwiOiBcImNvbnRleHQuaWRlbnRpdHkudXNlckFnZW50XCIsXG4gICAgICAgICAgXCJpbnRlZ3JhdGlvbi5yZXF1ZXN0LmhlYWRlci54LWRkLXByb3h5LXBhdGhcIjogXCJjb250ZXh0LnBhdGhcIixcbiAgICAgICAgICBcImludGVncmF0aW9uLnJlcXVlc3QuaGVhZGVyLngtZGQtYXBpZ3ctcHJvdG9jb2xcIjogXCJjb250ZXh0LnByb3RvY29sXCIsXG4gICAgICAgICAgXCJpbnRlZ3JhdGlvbi5yZXF1ZXN0LmhlYWRlci54LWRkLXByb3h5LXN0YWdlXCI6IFwiY29udGV4dC5zdGFnZVwiLFxuICAgICAgICB9XG4gICAgICB9LFxuICAgICAgdXJpOiBgaHR0cDovLyR7bG9hZEJhbGFuY2VyLmxvYWRCYWxhbmNlckRuc05hbWV9YCxcbiAgICB9KTtcblxuICAgIGNvbnN0IGFwaSA9IG5ldyBhcGlnYXRld2F5LlJlc3RBcGkodGhpcywgYCR7UkVTT1VSQ0VfSURfUFJFRklYX0NBTUVMX0NBU0V9LUFQSUdhdGV3YXlgLCB7XG4gICAgICByZXN0QXBpTmFtZTogYCR7UkVTT1VSQ0VfSURfUFJFRklYX0RBU0h9LWFwaS1nYXRld2F5YCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQVBJIEdhdGV3YXkgZm9yIGZvcndhcmRpbmcgcmVxdWVzdHMgdG8gQUxCJyxcbiAgICAgIGRlcGxveU9wdGlvbnM6IHsgc3RhZ2VOYW1lOiAncHJvZCcgfSxcbiAgICAgIGRlZmF1bHRJbnRlZ3JhdGlvbjogZW1wdHlJbnRlZ3JhdGlvbixcbiAgICB9KTtcblxuICAgIGFwaS5yb290LmFkZE1ldGhvZCgnQU5ZJywgZGRJbnRlZ3JhdGlvbik7XG4gICAgY29uc3QgYm9va3MgPSBhcGkucm9vdC5hZGRSZXNvdXJjZSgnYm9va3MnKTtcbiAgICBib29rcy5hZGRNZXRob2QoJ0FOWScpO1xuICAgIGNvbnN0IGJvb2sgPSBib29rcy5hZGRSZXNvdXJjZSgne2lkfScpO1xuICAgIGJvb2suYWRkTWV0aG9kKCdBTlknKTtcblxuICAgIC8vIE91dHB1dCB0aGUgdGFzayBwdWJsaWMgSVBcbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCBgJHtSRVNPVVJDRV9JRF9QUkVGSVhfQ0FNRUxfQ0FTRX0tRmFyZ2F0ZVNlcnZpY2VgLCB7XG4gICAgICB2YWx1ZTogc2VydmljZS5zZXJ2aWNlTmFtZSxcbiAgICAgIGRlc2NyaXB0aW9uOiAnTmFtZSBvZiB0aGUgRmFyZ2F0ZSBzZXJ2aWNlJyxcbiAgICB9KTtcblxuICAgIC8vIE91dHB1dCB0aGUgQUxCIEROUyBOYW1lXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0xvYWRCYWxhbmNlckROUycsIHtcbiAgICAgIHZhbHVlOiBsb2FkQmFsYW5jZXIubG9hZEJhbGFuY2VyRG5zTmFtZSxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQXBwbGljYXRpb24gTG9hZCBCYWxhbmNlciBETlMgTmFtZScsXG4gICAgfSk7XG5cbiAgICAvLyBPdXRwdXQgdGhlIEFMQiBTZWN1cml0eUdyb3VwXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0FsYlNlY3VyaXR5R3JvdXBJZCcsIHtcbiAgICAgIHZhbHVlOiBhbGJTZWN1cml0eUdyb3VwLnNlY3VyaXR5R3JvdXBJZCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQXBwbGljYXRpb24gTG9hZCBCYWxhbmNlciBETlMgTmFtZScsXG4gICAgfSk7XG5cbiAgICAvLyBPdXRwdXQgQVBJIEdhdGV3YXkgVVJMXG4gICAgbmV3IGNkay5DZm5PdXRwdXQodGhpcywgJ0FwaUdhdGV3YXlVUkwnLCB7XG4gICAgICB2YWx1ZTogYXBpLnVybCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQVBJIEdhdGV3YXkgVVJMJyxcbiAgICB9KTtcbiAgfVxufSBcblxuIl19