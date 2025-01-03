import { Handler } from 'aws-lambda';
import { sendDistributionMetric } from 'datadog-lambda-js';

export const handler: Handler = async (event, context) => {
    sendDistributionMetric('rey.ts.kittens', 1);
    return JSON.stringify(event, null, 2);
};
