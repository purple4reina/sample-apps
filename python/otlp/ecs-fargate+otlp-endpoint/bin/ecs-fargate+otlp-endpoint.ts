#!/opt/homebrew/opt/node/bin/node
import * as cdk from 'aws-cdk-lib';
import { EcsFargateOtlpEndpointStack } from '../lib/ecs-fargate+otlp-endpoint-stack';

const app = new cdk.App();
new EcsFargateOtlpEndpointStack(app, 'EcsFargateBillingUsingEndpointStack',
  {
    env: {
      account: process.env.CDK_DEFAULT_ACCOUNT,
      region: "sa-east-1",
    },
  },
  {
    prefix: 'otlp-billing-',
    apiKey: process.env.DD_STAGING_OTLP_API_KEY || '',
    site: process.env.DD_STAGING_OTLP_SITE || '',
  },
);
