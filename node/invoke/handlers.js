const { InvokeCommand, LambdaClient } = require('@aws-sdk/client-lambda');
const lambdaClient = new LambdaClient();

exports.client = async function(event, context) {
  const response = await lambdaClient.send(new InvokeCommand({
    FunctionName: process.env.LAMBDA_ARN,
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ hello: "rey" }),
  }));
  return {
    statusCode: 200,
    body: JSON.stringify(response.Payload),
  };
}

exports.server = async function(event, context) {
  console.log("Server handler invoked with event:", event);
  return JSON.stringify(event);
}
