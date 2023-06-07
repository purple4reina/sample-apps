var coldStart = true;

exports.handler = async function(event, context) {
  try {
    return { cold_start: coldStart }
  } finally {
    coldStart = false;
  }
}

if (process.env._HANDLER) {
  const datadog = require('datadog-lambda-js');
  exports.handler = datadog.datadog(exports.handler);
}
