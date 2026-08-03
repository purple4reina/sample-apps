'use strict';

// Settlement producer.
//
// Invoked on a schedule (EventBridge) and on demand (direct invoke). Each run
// emits a batch of settlement messages onto the queue. The wire format is
// chosen per message: the current "format generation" is read from an SSM
// parameter, and when it is anything other than `stable`, a configurable
// fraction of the batch is emitted in that generation to simulate a gradual
// upstream rollout (so both the old and new formats coexist in traffic).

const { SQSClient, SendMessageBatchCommand } = require('@aws-sdk/client-sqs');
const { SSMClient, GetParameterCommand } = require('@aws-sdk/client-ssm');
const { buildMessage } = require('./format');

const sqs = new SQSClient({});
const ssm = new SSMClient({});

const QUEUE_URL = process.env.QUEUE_URL;
const FORMAT_PARAM_NAME = process.env.FORMAT_PARAM_NAME;
const BATCH_SIZE = parseInt(process.env.BATCH_SIZE || '60', 10);
const DRIFT_RATIO = parseFloat(process.env.DRIFT_RATIO || '0.4');

async function currentGeneration() {
  try {
    const res = await ssm.send(new GetParameterCommand({ Name: FORMAT_PARAM_NAME }));
    return (res.Parameter && res.Parameter.Value) || 'stable';
  } catch (err) {
    return 'stable';
  }
}

exports.handler = async () => {
  const generation = await currentGeneration();

  const messages = [];
  for (let i = 0; i < BATCH_SIZE; i++) {
    const useNextFormat = generation !== 'stable' && Math.random() < DRIFT_RATIO;
    messages.push(buildMessage(useNextFormat ? generation : 'stable'));
  }

  let sent = 0;
  for (let i = 0; i < messages.length; i += 10) {
    const chunk = messages.slice(i, i + 10);
    await sqs.send(
      new SendMessageBatchCommand({
        QueueUrl: QUEUE_URL,
        Entries: chunk.map((m, j) => ({ Id: String(i + j), MessageBody: JSON.stringify(m) })),
      })
    );
    sent += chunk.length;
  }

  return { emitted: sent, generation };
};
