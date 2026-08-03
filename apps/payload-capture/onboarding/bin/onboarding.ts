#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ReyOnboardingStack } from '../lib/onboarding-stack';

const app = new cdk.App();
new ReyOnboardingStack(app, 'ReyOnboardingStack', {
  env: {
    region: 'sa-east-1',
  },
});
