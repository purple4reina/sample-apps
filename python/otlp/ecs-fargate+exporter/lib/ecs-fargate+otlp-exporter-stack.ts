import * as aws_ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import { Construct } from 'constructs';

export class EcsFargateOtlpExporterStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps, opts?: any) {
    super(scope, id, props);
    const pfx = opts.prefix || '';

    const vpc = ec2.Vpc.fromLookup(this, pfx+'DefaultVpc', { isDefault: true });
    const cluster = new ecs.Cluster(this, pfx+'AppCluster', { vpc });

    // Create task definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, pfx+'TaskDef', {
      cpu: 512,
      memoryLimitMiB: 1024,
    });

    // Add OpenTelemetry Collector container
    const collectorContainer = taskDefinition.addContainer(pfx+'OtelCollector', {
      image: ecs.ContainerImage.fromAsset('./collector', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      essential: true,
      environment: {
        DD_API_KEY: opts.apiKey,
        DD_SITE: opts.site,
      },
      command: ['--config=config.yml'],
      portMappings: [{ containerPort: 4318 }],
      logging: new ecs.AwsLogDriver({ streamPrefix: pfx+'collector' }),
    });

    // Add application container
    const appContainer = taskDefinition.addContainer(pfx+'FlaskApp', {
      image: ecs.ContainerImage.fromAsset('./app', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      environment: {
        OTEL_ENVIRONMENT: 'prod',
        OTEL_EXPORTER_OTLP_ENDPOINT: 'http://localhost:4318',
        OTEL_EXPORTER_OTLP_PROTOCOL: 'http/protobuf',
        OTEL_METRICS_EXPORTER: 'none',
        OTEL_PYTHON_LOG_LEVEL: 'debug',
        OTEL_SERVICE_NAME: 'otlp-billing-fargate-exporter',
        OTEL_SERVICE_VERSION: '1.0.0',
      },
      portMappings: [{ containerPort: 8080 }],
      logging: new ecs.AwsLogDriver({ streamPrefix: pfx+'app' }),
    });

    // App depends on collector being ready
    appContainer.addContainerDependencies({
      container: collectorContainer,
      condition: ecs.ContainerDependencyCondition.START,
    });

    // Add traffic producing container
    const trafficContainer = taskDefinition.addContainer(pfx+'Traffic', {
      image: ecs.ContainerImage.fromAsset('./traffic', {
        platform: aws_ecr_assets.Platform.LINUX_AMD64,
      }),
      command: ['./start.sh'],
      logging: new ecs.AwsLogDriver({ streamPrefix: pfx+'traffic' }),
    });

    // Traffic depends on app being ready
    trafficContainer.addContainerDependencies({
      container: appContainer,
      condition: ecs.ContainerDependencyCondition.START,
    });

    // Create the service without a load balancer
    const fargateService = new ecs.FargateService(this, pfx+'FlaskService', {
      cluster,
      taskDefinition,
      desiredCount: 1,
      assignPublicIp: true,
    });
  }
}
