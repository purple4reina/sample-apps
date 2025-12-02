import * as aws_ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as eks from 'aws-cdk-lib/aws-eks';
import { KubectlV30Layer } from '@aws-cdk/lambda-layer-kubectl-v30';
import { Construct } from 'constructs';

export class ReyEksFargateOtlpExporterStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Use existing VPC (created once, reused for simplicity)
    const vpc = ec2.Vpc.fromLookup(this, 'ReyVpc', {
      vpcId: 'vpc-08ef5c5adf9b0a93e',
    });

    // Create EKS cluster
    const cluster = new eks.Cluster(this, 'ReyAppCluster', {
      vpc,
      version: eks.KubernetesVersion.V1_30,
      defaultCapacity: 0, // No EC2 nodes, only Fargate
      clusterName: `rey-otlp-test-cluster-${cdk.Names.uniqueId(this).slice(-8).toLowerCase()}`,
      kubectlLayer: new KubectlV30Layer(this, 'ReyKubectlLayer'),
    });

    // Add Fargate profile for our app
    const fargateProfile = cluster.addFargateProfile('ReyFargateProfile', {
      selectors: [{ namespace: 'otlp-test' }],
      fargateProfileName: 'otlp-test-profile',
    });

    // Build and push container images to ECR
    const collectorImage = new aws_ecr_assets.DockerImageAsset(this, 'ReyCollectorImage', {
      directory: './collector',
      platform: aws_ecr_assets.Platform.LINUX_AMD64,
    });

    const appImage = new aws_ecr_assets.DockerImageAsset(this, 'ReyAppImage', {
      directory: './app',
      platform: aws_ecr_assets.Platform.LINUX_AMD64,
    });

    const trafficImage = new aws_ecr_assets.DockerImageAsset(this, 'ReyTrafficImage', {
      directory: './traffic',
      platform: aws_ecr_assets.Platform.LINUX_AMD64,
    });

    // Create namespace
    const namespace = cluster.addManifest('ReyNamespace', {
      apiVersion: 'v1',
      kind: 'Namespace',
      metadata: {
        name: 'otlp-test',
        labels: {
          app: 'otlp-test',
        },
      },
    });

    // Create ConfigMap for OTEL collector config
    const collectorConfig = cluster.addManifest('ReyCollectorConfig', {
      apiVersion: 'v1',
      kind: 'ConfigMap',
      metadata: {
        name: 'otel-collector-config',
        namespace: 'otlp-test',
      },
      data: {
        'config.yml': `receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  debug:
  datadog/exporter:
    api:
      key: \${env:DD_API_KEY}
      site: \${env:DD_SITE}

processors:
  resourcedetection/eks:
    detectors: [env, system, eks]
    timeout: 2s
    override: false

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [resourcedetection/eks]
      exporters: [debug, datadog/exporter]
`,
      },
    });
    collectorConfig.node.addDependency(namespace);

    // Create Deployment with all 3 containers
    const deployment = cluster.addManifest('ReyDeployment', {
      apiVersion: 'apps/v1',
      kind: 'Deployment',
      metadata: {
        name: 'otlp-test-app',
        namespace: 'otlp-test',
      },
      spec: {
        replicas: 1,
        selector: {
          matchLabels: {
            app: 'otlp-test-app',
          },
        },
        template: {
          metadata: {
            labels: {
              app: 'otlp-test-app',
            },
          },
          spec: {
            containers: [
              // OpenTelemetry Collector
              {
                name: 'otel-collector',
                image: collectorImage.imageUri,
                command: ['/otelcol-contrib'],
                args: ['--config=/etc/otel/config.yml'],
                ports: [
                  {
                    containerPort: 4318,
                    name: 'otlp-http',
                  },
                ],
                env: [
                  {
                    name: 'DD_API_KEY',
                    value: process.env.DD_API_KEY || '',
                  },
                  {
                    name: 'DD_SITE',
                    value: process.env.DD_SITE || 'datadoghq.com',
                  },
                ],
                volumeMounts: [
                  {
                    name: 'otel-collector-config',
                    mountPath: '/etc/otel',
                  },
                ],
                resources: {
                  requests: {
                    memory: '256Mi',
                    cpu: '100m',
                  },
                  limits: {
                    memory: '512Mi',
                    cpu: '200m',
                  },
                },
              },
              // Flask Application
              {
                name: 'flask-app',
                image: appImage.imageUri,
                ports: [
                  {
                    containerPort: 8080,
                    name: 'http',
                  },
                ],
                env: [
                  {
                    name: 'OTEL_ENVIRONMENT',
                    value: 'prod',
                  },
                  {
                    name: 'OTEL_EXPORTER_OTLP_ENDPOINT',
                    value: 'http://localhost:4318',
                  },
                  {
                    name: 'OTEL_EXPORTER_OTLP_PROTOCOL',
                    value: 'http/protobuf',
                  },
                  {
                    name: 'OTEL_METRICS_EXPORTER',
                    value: 'none',
                  },
                  {
                    name: 'OTEL_PYTHON_LOG_LEVEL',
                    value: 'debug',
                  },
                  {
                    name: 'OTEL_SERVICE_NAME',
                    value: 'rey-eks-fargate',
                  },
                  {
                    name: 'OTEL_SERVICE_VERSION',
                    value: '1.0.0',
                  },
                ],
                resources: {
                  requests: {
                    memory: '256Mi',
                    cpu: '100m',
                  },
                  limits: {
                    memory: '512Mi',
                    cpu: '200m',
                  },
                },
              },
              // Traffic Generator
              {
                name: 'traffic-generator',
                image: trafficImage.imageUri,
                command: ['/bin/bash', '-c'],
                args: [
                  'while true; do curl http://localhost:8080; sleep 30; done',
                ],
                resources: {
                  requests: {
                    memory: '64Mi',
                    cpu: '50m',
                  },
                  limits: {
                    memory: '128Mi',
                    cpu: '100m',
                  },
                },
              },
            ],
            volumes: [
              {
                name: 'otel-collector-config',
                configMap: {
                  name: 'otel-collector-config',
                },
              },
            ],
          },
        },
      },
    });
    deployment.node.addDependency(collectorConfig);
    deployment.node.addDependency(fargateProfile);
  }
}
