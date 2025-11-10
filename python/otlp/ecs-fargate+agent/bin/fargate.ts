#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ReyFargeteExporterStack } from '../lib/fargate-stack';
import { execSync } from 'child_process';

const app = new cdk.App();
const env = {
  region: "sa-east-l",
  account: execSync("aws sts get-caller-identity --query 'Account' --output text").toString().trim(),
};
new ReyFargeteExporterStack(app, 'ReyFargeteExporterStack', { env: env });
