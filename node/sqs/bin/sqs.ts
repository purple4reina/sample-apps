#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { SqsStack } from '../lib/sqs-stack';

const app = new cdk.App();
new SqsStack(app, 'SqsStack');
