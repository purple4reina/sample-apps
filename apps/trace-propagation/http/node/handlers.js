const tracer = require('dd-trace').init();
const { sendDistributionMetric } = require('datadog-lambda-js');

const serverUrls = process.env.SERVER_URLS.split(',');
const runtime = process.env.AWS_EXECUTION_ENV.replace('AWS_Lambda_', '');

exports.client = async function(event, context) {
  data = JSON.stringify({
    runtime: runtime,
    trace_id: currentTraceId(),
  });
  for (url of serverUrls) {
    console.log(`calling ${url} with data ${data}`);
    await fetch(url, {body: data});
  }
  return {'statusCode': 200, 'body': 'ok'};
}

exports.server = async function(event, context) {
  const traceId = currentTraceId();
  const { body } = event;
  console.log(`received http data ${body}`);
  payload = JSON.parse(body);
  sendDistributionMetric(
    'trace_context.propagated.http', 1,
    `server_runtime:${runtime}`,
    `client_runtime:${payload.runtime}`,
    traceId == payload.trace_id ? 'success:true' : 'success:false',
    'transport:http',
  );
  return {'statusCode': 200, 'body': 'ok'};
}

function currentTraceId() {
  const ctx = tracer.scope().active()?.context();
  console.log(`found trace context: traceId=${ctx.toTraceId()} spanId=${ctx.toSpanId()}`);
  return ctx.toTraceId();
}
