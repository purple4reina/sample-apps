'use strict';

// Storefront producer.
//
// Invoked on a schedule (EventBridge) and on demand (direct invoke). Each run
// emits a batch of `order.placed` events onto the queue. Unlike the incident
// app's producer, there is no format toggle here — every event is built the
// same way, in the same steady healthy shape.

const { SQSClient, SendMessageBatchCommand } = require('@aws-sdk/client-sqs');
const { buildOrderPlacedEvent } = require('./order');

const sqs = new SQSClient({});

const QUEUE_URL = process.env.QUEUE_URL;
const BATCH_SIZE = parseInt(process.env.BATCH_SIZE || '30', 10);

exports.handler = async () => {
  const events = Array.from({ length: BATCH_SIZE }, buildOrderPlacedEvent);

  let sent = 0;
  for (let i = 0; i < events.length; i += 10) {
    const chunk = events.slice(i, i + 10);
    await sqs.send(
      new SendMessageBatchCommand({
        QueueUrl: QUEUE_URL,
        Entries: chunk.map((e, j) => ({ Id: String(i + j), MessageBody: JSON.stringify(e) })),
      })
    );
    sent += chunk.length;
  }

  return { emitted: sent };
};
