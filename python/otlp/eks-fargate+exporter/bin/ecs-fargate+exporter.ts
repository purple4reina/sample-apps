#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { ReyEksFargateOtlpExporterStack } from '../lib/eks-fargate+otlp-exporter-stack';

const app = new cdk.App();
new ReyEksFargateOtlpExporterStack(app, 'ReyEksFargateOtlpExporterStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: "sa-east-1",
  },
});
