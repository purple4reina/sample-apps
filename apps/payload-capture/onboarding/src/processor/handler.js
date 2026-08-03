'use strict';

// Storefront processor.
//
// Triggered by SQS, one message at a time (batchSize: 1) so that one placed
// order maps to exactly one invocation, and therefore one captured payload.

const { summarizeOrder } = require('./order-summary');

exports.handler = async (event) => {
  const summaries = [];
  for (const record of event.Records) {
    const order = JSON.parse(record.body);
    summaries.push(summarizeOrder(order));
  }
  return { processed: event.Records.length, summaries };
};
