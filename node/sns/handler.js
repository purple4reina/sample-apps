const tracer = require('dd-trace');

const AWS = require('aws-sdk');
const sns = new AWS.SNS();

const sleep = tracer.wrap('sleep', (ms) => {
  return new Promise(r => setTimeout(r, ms));
});

exports.producer = async function(event, context) {
  const params = {
    Message: JSON.stringify({ message: 'Hello from SNS' }),
    TopicArn: process.env.TOPIC_ARN
  };

  await sns.publish(params).promise();
  return params;
}

exports.consumer = async function(event, context) {
  console.log(JSON.stringify(event));
  await sleep(1000);
  return event;
}
