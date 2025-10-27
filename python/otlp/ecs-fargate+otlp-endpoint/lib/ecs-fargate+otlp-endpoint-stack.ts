import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as aws_ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';

export class ReyEcsFargateOtlpEndpointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = ec2.Vpc.fromLookup(this, 'ReyDefaultVpc', { isDefault: true });
    const cluster = new ecs.Cluster(this, 'ReyAppCluster', { vpc });

    const availabilityZones = Array.from(new Set(vpc.publicSubnets.map(s => s.availabilityZone)));
    const uniqueSubnets = availabilityZones.map(az =>
      vpc.publicSubnets.find(s => s.availabilityZone === az)!
    );

    const alb = new elbv2.ApplicationLoadBalancer(this, 'ReyALB', {
      vpc,
      internetFacing: true,
      vpcSubnets: { subnets: uniqueSubnets },
    });

    const fargateService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'ReyFlaskService', {
      cluster,
      loadBalancer: alb,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset('./app', {
          platform: aws_ecr_assets.Platform.LINUX_AMD64,
        }),
        containerPort: 8080,
      },
      desiredCount: 1,
      cpu: 256,
      memoryLimitMiB: 1024,
      assignPublicIp: true,
    });

    new cdk.CfnOutput(this, 'URL', { value: `http://${fargateService.loadBalancer.loadBalancerDnsName}` });
  }
}
