const datadog = require('dd-trace').init({});

const AWS = require('aws-sdk');
const sns = new AWS.SNS();

exports.producer = async function(event, context) {
  const params = {
    Message: JSON.stringify({ message: 'Hello from SNS' }),
    TopicArn: process.env.TOPIC_ARN
  };

  await sns.publish(params).promise();
  return params;
}

exports.consumer = async function(event, context) {
  console.log('Event:', event);
  const span = datadog.tracer.startSpan('consumer');
  await new Promise(resolve => setTimeout(resolve, 100));
  span.finish();
  return event;
}
