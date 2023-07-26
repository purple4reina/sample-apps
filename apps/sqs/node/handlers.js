const tracer = require('dd-trace').init();

const { SQSClient, SendMessageCommand } = require("@aws-sdk/client-sqs");
const client = new SQSClient();

const queueUrls = process.env.SQS_QUEUE_URLS.split(',');
const runtime = process.env.AWS_EXECUTION_ENV.replace('AWS_Lambda_', '');

exports.producer = async function(event, context) {
  msg = JSON.stringify({
    runtime: runtime,
    trace_id: currentTraceId(),
  })
  for (url of queueUrls) {
    console.log(`sending sqs message ${msg} to ${url}`);
    await client.send(new SendMessageCommand({
      MessageBody: msg,
      QueueUrl: url,
    }));
  }
  return {'statusCode': 200, 'body': 'ok'};
}

function currentTraceId() {
  const ctx = tracer.scope().active()?.context();
  console.log(`found trace context: traceId=${ctx.toTraceId()} spanId=${ctx.toSpanId()}`);
  return ctx.toTraceId();
}
