const hotshots = require('hot-shots');
const statsDClient = new hotshots.StatsD({ host: "127.0.0.1", closingFlushInterval: 1 });
const tags = {
  'service': 'hello-extension-REY-1',
  'whatever': 'is-fine-to-be-honest',
}

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

exports.hello = function(event, context) {
  console.log('hello world!');
  statsDClient.distribution('serverless.node.custom_metric', getRandomInt(100),
    undefined, tags);
  return {'hello': 'world'}
}
