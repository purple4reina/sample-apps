#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ReyPayloadCaptureStack } from '../lib/payload-capture-stack';

const app = new cdk.App();
new ReyPayloadCaptureStack(app, 'ReyPayloadCaptureStack', {
  env: {
    region: 'sa-east-1',
  },
});
