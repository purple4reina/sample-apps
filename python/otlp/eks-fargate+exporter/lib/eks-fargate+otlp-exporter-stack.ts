import * as aws_ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import { Construct } from 'constructs';

export class ReyEksFargateOtlpExporterStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = ec2.Vpc.fromLookup(this, 'ReyDefaultVpc', { isDefault: true });
    const cluster = new ecs.Cluster(this, 'ReyAppCluster', { vpc });

    // Create task definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'ReyTaskDef', {
      cpu: 512,
      memoryLimitMiB: 1024,
    });

    // Add OpenTelemetry Collector container
    const collectorContainer = taskDefinition.addContainer('ReyOtelCollector', {
      image: ecs.ContainerImage.fromAsset('./collector', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      essential: true,
      environment: {
        DD_API_KEY: process.env.DD_API_KEY || '',
        DD_SITE: process.env.DD_SITE || 'datadoghq.com',
      },
      command: ['--config=config.yml'],
      portMappings: [{ containerPort: 4318 }],
      logging: new ecs.AwsLogDriver({ streamPrefix: 'rey-collector' }),
    });

    // Add application container
    const appContainer = taskDefinition.addContainer('ReyFlaskApp', {
      image: ecs.ContainerImage.fromAsset('./app', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      environment: {
        OTEL_ENVIRONMENT: 'prod',
        OTEL_EXPORTER_OTLP_ENDPOINT: 'http://localhost:4318',
        OTEL_EXPORTER_OTLP_PROTOCOL: 'http/protobuf',
        OTEL_METRICS_EXPORTER: 'none',
        OTEL_PYTHON_LOG_LEVEL: 'debug',
        OTEL_SERVICE_NAME: 'rey-ecs-fargate',
        OTEL_SERVICE_VERSION: '1.0.0',
      },
      portMappings: [{ containerPort: 8080 }],
      logging: new ecs.AwsLogDriver({ streamPrefix: 'rey-app' }),
    });

    // App depends on collector being ready
    appContainer.addContainerDependencies({
      container: collectorContainer,
      condition: ecs.ContainerDependencyCondition.START,
    });

    // Add traffic producing container
    const trafficContainer = taskDefinition.addContainer('ReyTraffic', {
      image: ecs.ContainerImage.fromAsset('./traffic', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      command: ['./start.sh'],
      logging: new ecs.AwsLogDriver({ streamPrefix: 'rey-traffic' }),
    });

    // Traffic depends on app being ready
    trafficContainer.addContainerDependencies({
      container: appContainer,
      condition: ecs.ContainerDependencyCondition.START,
    });

    // Create the service without a load balancer
    const fargateService = new ecs.FargateService(this, 'ReyFlaskService', {
      cluster,
      taskDefinition,
      desiredCount: 1,
      assignPublicIp: true,
    });
  }
}
