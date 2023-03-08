var coldStart = true;

exports.handler = async function(event, context) {
  try {
    return { cold_start: coldStart }
  } finally {
    coldStart = false;
  }
}
