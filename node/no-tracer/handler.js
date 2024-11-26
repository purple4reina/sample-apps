const datadog = require('datadog-lambda-js');

async function handler(event, context) {
  console.log("ok");
  return "ok";
}

exports.handler = datadog.datadog(handler);
