const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer();

var coldStart = true;

exports.handler = async function (event) {
  try {
    await tracer.startActiveSpan('function', async (span) => {
      await sleep(1000);
      span.end();
    });
    return {
      statusCode: 200,
      body: JSON.stringify({
        "cold_start": coldStart,
      }),
    };
  } finally {
    coldStart = false;
  }
};

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};
