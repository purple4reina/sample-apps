'use strict';

// Settlement processor.
//
// Triggered by SQS, one message at a time. Each message carries a single
// settlement instruction which is handed to the processing pipeline. A message
// that cannot be processed is thrown back to SQS, which retries it and, after
// the redrive limit, routes it to the dead-letter queue.

const { processSettlement } = require('./settlement');

exports.handler = async (event) => {
  for (const record of event.Records) {
    const message = JSON.parse(record.body);
    try {
      processSettlement(message);
    } catch (err) {
      console.error(`settlement ${message.messageId} rejected: ${err.message}`);
      throw err;
    }
  }
  return { processed: event.Records.length };
};
