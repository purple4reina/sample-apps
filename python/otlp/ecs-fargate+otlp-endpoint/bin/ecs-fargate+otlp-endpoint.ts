#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { ReyEcsFargateOtlpEndpointStack } from '../lib/ecs-fargate+otlp-endpoint-stack';

const app = new cdk.App();
new ReyEcsFargateOtlpEndpointStack(app, 'ReyEcsFargateOtlpEndpointStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: "sa-east-1",
  },
});
