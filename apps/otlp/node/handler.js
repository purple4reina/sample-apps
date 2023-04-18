const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer();

var coldStart = true;

exports.handler = async function (event) {
  try {
    await tracer.startActiveSpan('handler', async (span) => {
      await tracer.startActiveSpan('function', async (spanChild) => {
        await sleep(1000);
        spanChild.end();
      });
      span.end();
    });
    return {
      statusCode: 200,
      body: JSON.stringify({
        "cold_start": coldStart,
        "runtime": "node",
      }),
    };
  } finally {
    coldStart = false;
  }
};

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};
