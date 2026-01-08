exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    body: JSON.stringify({ event, context }),
  };
}

exports.authorizer = async function(event, context) {
  console.log(event);
  let token;
  let methodArn;
  if (event.type === 'REQUEST') {
    token = (event.headers || {}).Authorization ? event.headers.Authorization.slice(7) : ''; // Skip 'Bearer '
    methodArn = event.methodArn;
  } else {
    token = event.authorizationToken ? event.authorizationToken.slice(7) : '';
    methodArn = event.methodArn;
  }
  return {
    principalId: 'user',
    policyDocument: {
      Version: '2012-10-17',
      Statement: [
        {
          Action: 'execute-api:Invoke',
          Effect: token ? 'Allow' : 'Deny',
          Resource: [methodArn || '*'],
        }
      ]
    }
  };
}
