#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { ReyEcsFargateOtlpExporterStack } from '../lib/ecs-fargate+otlp-exporter-stack';

const app = new cdk.App();
new ReyEcsFargateOtlpExporterStack(app, 'ReyEcsFargateOtlpExporterStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: "sa-east-1",
  },
});
