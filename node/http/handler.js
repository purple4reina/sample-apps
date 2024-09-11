const tracer = require('dd-trace');

const sleep = tracer.wrap('sleep', (ms) => {
    return new Promise((r) => setTimeout(r, ms));
});

exports.client = async function(event, context) {
  const url = process.env.SERVER_URL;
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${url}`);
  }
  return { body: await resp.text() }
}

exports.server = async function(event, context) {
  await sleep(1000);
  return { body: 'Hello from server' }
}
