#
# Find more info at https://godoc.org/github.com/aws/aws-lambda-go/events
#

S3_EVENT = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "1970-01-01T00:00:00.123Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "C3D13FE58DE4C810",
        "x-amz-id-2": "FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "sourcebucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::mybucket"
        },
        "object": {
          "key": "HappyFace.jpg",
          "size": 1024,
          "urlDecodedKey": "HappyFace.jpg",
          "versionId": "version",
          "eTag": "d41d8cd98f00b204e9800998ecf8427e",
          "sequencer": "Happy Sequencer"
        }
      }
    }
  ]
}

CLOUDWATCH_EVENT = {
  "account": "123456789012",
  "region": "us-east-1",
  "detail-type": "CodeDeploy Instance State-change Notification",
  "source": "aws.codedeploy",
  "version": "0",
  "time": "2016-06-30T23:18:50Z",
  "id": "fb1d3015-c091-4bf9-95e2-d98521ab2ecb",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-0000000aaaaaaaaaa",
    "arn:aws:codedeploy:us-east-1:123456789012:deploymentgroup:myApplication/myDeploymentGroup",
    "arn:aws:codedeploy:us-east-1:123456789012:application:myApplication"
  ],
  "detail": {
    "instanceId": "i-0000000aaaaaaaaaa",
    "region": "us-east-1",
    "state": "SUCCESS",
    "application": "myApplication",
    "deploymentId": "d-123456789",
    "instanceGroupId": "8cd3bfa8-9e72-4cbe-a1e5-da4efc7efd49",
    "deploymentGroup": "myDeploymentGroup"
  }
}

CLOUDWATCH_LOGS_EVENT = {  # represents raw data from a cloudwatch logs event
  "awslogs": {
    # "data" contains gzipped base64 json representing the bulk of a cloudwatch
    # logs event. It will unmarshall into
    # https://github.com/aws/aws-lambda-go/blob/master/events/cloudwatch_logs.go
    "data": "H4sIAAAAAAAAAHWPwQqCQBCGX0Xm7EFtK+smZBEUgXoLCdMhFtKV3akI8d0bLYmibvPPN3wz00CJxmQnTO41whwWQRIctmEcB6sQbFC3CjW3XW8kxpOpP+OC22d1Wml1qZkQGtoMsScxaczKN3plG8zlaHIta5KqWsozoTYw3/djzwhpLwivWFGHGpAFe7DL68JlBUk+l7KSN7tCOEJ4M3/qOI49vMHj+zCKdlFqLaU2ZHV2a4Ct/an0/ivdX8oYc1UVX860fQDQiMdxRQEAAA=="
  }
}

KINESIS_EVENT = {
  "Records": [
    {
        "kinesis": {
          "kinesisSchemaVersion": "1.0",
          "partitionKey": "s1",
          "sequenceNumber": "49568167373333333333333333333333333333333333333333333333",
          "data": "SGVsbG8gV29ybGQ=",
          "approximateArrivalTimestamp": 1480641523.477
        },
        "eventSource": "aws:kinesis",
        "eventVersion": "1.0",
        "eventID": "shardId-000000000000:49568167373333333333333333333333333333333333333333333333",
        "eventName": "aws:kinesis:record",
        "invokeIdentityArn": "arn:aws:iam::123456789012:role/LambdaRole",
        "awsRegion": "us-east-1",
        "eventSourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/simple-stream"
    },
    {
        "kinesis": {
          "kinesisSchemaVersion": "1.0",
          "partitionKey": "s1",
          "sequenceNumber": "49568167373333333334444444444444444444444444444444444444",
          "data": "SGVsbG8gV29ybGQ=",
          "approximateArrivalTimestamp": 1480841523.477
        },
        "eventSource": "aws:kinesis",
        "eventVersion": "1.0",
        "eventID": "shardId-000000000000:49568167373333333334444444444444444444444444444444444444",
        "eventName": "aws:kinesis:record",
        "invokeIdentityArn": "arn:aws:iam::123456789012:role/LambdaRole",
        "awsRegion": "us-east-1",
        "eventSourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/simple-stream"
    }
  ]
}

KINESIS_FIREHOSE_EVENT = {
   "invocationId": "invoked123",
   "deliveryStreamArn": "aws:lambda:events",
   "region": "us-west-2",
   "records": [
     {
       "data": "SGVsbG8gV29ybGQ=",
       "recordId": "record1",
       "approximateArrivalTimestamp": 1507217624302,
       "kinesisRecordMetadata": {
         "shardId": "shardId-000000000000",
         "partitionKey": "4d1ad2b9-24f8-4b9d-a088-76e9947c317a",
         "approximateArrivalTimestamp": "1507217624302",
         "sequenceNumber": "49546986683135544286507457936321625675700192471156785154",
         "subsequenceNumber": ""
       }
     },
     {
       "data": "SGVsbG8gV29ybGQ=",
       "recordId": "record2",
       "approximateArrivalTimestamp": 1507217624302,
       "kinesisRecordMetadata": {
         "shardId": "shardId-000000000001",
         "partitionKey": "4d1ad2b9-24f8-4b9d-a088-76e9947c318a",
         "approximateArrivalTimestamp": "1507217624302",
         "sequenceNumber": "49546986683135544286507457936321625675700192471156785155",
         "subsequenceNumber": ""
       }
     }
   ]
 }

API_GATEWAY_REQUEST = {
  "resource": "/{proxy+}",
    "path": "/hello/world",
    "httpMethod": "POST",
    "headers": {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate",
      "cache-control": "no-cache",
      "CloudFront-Forwarded-Proto": "https",
      "CloudFront-Is-Desktop-Viewer": "true",
      "CloudFront-Is-Mobile-Viewer": "false",
      "CloudFront-Is-SmartTV-Viewer": "false",
      "CloudFront-Is-Tablet-Viewer": "false",
      "CloudFront-Viewer-Country": "US",
      "Content-Type": "application/json",
      "headerName": "headerValue",
      "Host": "gy415nuibc.execute-api.us-east-1.amazonaws.com",
      "Postman-Token": "9f583ef0-ed83-4a38-aef3-eb9ce3f7a57f",
      "User-Agent": "PostmanRuntime/2.4.5",
      "Via": "1.1 d98420743a69852491bbdea73f7680bd.cloudfront.net (CloudFront)",
      "X-Amz-Cf-Id": "pn-PWIJc6thYnZm5P0NMgOUglL1DYtl0gdeJky8tqsg8iS_sgsKD1A==",
      "X-Forwarded-For": "54.240.196.186, 54.182.214.83",
      "X-Forwarded-Port": "443",
      "X-Forwarded-Proto": "https"
  },
  "queryStringParameters": {
    "name": "me"
  },
  "pathParameters": {
    "proxy": "hello/world"
  },
  "stageVariables": {
    "stageVariableName": "stageVariableValue"
  },
  "requestContext": {
    "accountId": "12345678912",
    "resourceId": "roq9wj",
    "stage": "testStage",
    "requestId": "deef4878-7910-11e6-8f14-25afc3e9ae33",
    "identity": {
      "cognitoIdentityPoolId": "theCognitoIdentityPoolId",
      "accountId": "theAccountId",
      "cognitoIdentityId": "theCognitoIdentityId",
      "caller": "theCaller",
      "apiKey": "theApiKey",
      "sourceIp": "192.168.196.186",
      "cognitoAuthenticationType": "theCognitoAuthenticationType",
      "cognitoAuthenticationProvider": "theCognitoAuthenticationProvider",
      "userArn": "theUserArn",
      "userAgent": "PostmanRuntime/2.4.5",
      "user": "theUser"
    },
    "authorizer": {
      "principalId": "admin",
      "clientId": 1,
      "clientName": "Exata"
    },
    "resourcePath": "/{proxy+}",
    "httpMethod": "POST",
    "apiId": "gy415nuibc"
  },
  "body": "{\r\n\t\"a\": 1\r\n}"
}

API_GATEWAY_CUSTOM_AUTHORIZER_REQUEST = {
    "type": "TOKEN",
    "authorizationToken": "allow",
    "methodArn": "arn:aws:execute-api:us-west-2:123456789012:ymy8tbxw7b/*/GET/"
}


DYNAMODB_EVENT = {
  "Records": [
    {
      "eventID": "f07f8ca4b0b26cb9c4e5e77e69f274ee",
      "eventName": "INSERT",
      "eventVersion": "1.1",
      "eventSource": "aws:dynamodb",
      "awsRegion": "us-east-1",
      "userIdentity":{
        "type":"Service",
        "principalId":"dynamodb.amazonaws.com"
      },
      "dynamodb": {
        "ApproximateCreationDateTime": 1480642020,
        "Keys": {
          "val": {
            "S": "data"
          },
          "key": {
            "S": "binary"
          }
        },
        "NewImage": {
          "val": {
            "S": "data"
          },
          "asdf1": {
            "B": "AAEqQQ=="
          },
          "asdf2": {
            "BS": [
              "AAEqQQ==",
              "QSoBAA=="
            ]
          },
          "key": {
            "S": "binary"
          }
        },
        "SequenceNumber": "1405400000000002063282832",
        "SizeBytes": 54,
        "StreamViewType": "NEW_AND_OLD_IMAGES"
      },
      "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/Example-Table/stream/2016-12-01T00:00:00.000"
    },
    {
      "eventID": "f07f8ca4b0b26cb9c4e5e77e42f274ee",
      "eventName": "INSERT",
      "eventVersion": "1.1",
      "eventSource": "aws:dynamodb",
      "awsRegion": "us-east-1",
      "dynamodb": {
        "ApproximateCreationDateTime": 1480642020,
        "Keys": {
          "val": {
            "S": "data"
          },
          "key": {
            "S": "binary"
          }
        },
        "NewImage": {
          "val": {
            "S": "data"
          },
          "asdf1": {
            "B": "AAEqQQ=="
          },
          "b2": {
            "B": "test"
          },
          "asdf2": {
            "BS": [
              "AAEqQQ==",
              "QSoBAA==",
              "AAEqQQ=="
            ]
          },
          "key": {
            "S": "binary"
          },
          "Binary": {
            "B": "AAEqQQ=="
          },
          "Boolean": {
            "BOOL": True
          },
          "BinarySet": {
            "BS": [
              "AAEqQQ==",
              "AAEqQQ=="
            ]
          },
          "List": {
            "L": [
              {
                "S": "Cookies"
              },
              {
                "S": "Coffee"
              },
              {
                "N": "3.14159"
              }
            ]
          },
          "Map": {
            "M": {
              "Name": {
                "S": "Joe"
              },
              "Age": {
                "N": "35"
              }
            }
          },
          "FloatNumber": {
            "N": "123.45"
          },
          "IntegerNumber": {
            "N": "123"
          },
          "NumberSet": {
            "NS": [
              "1234",
              "567.8"
            ]
          },
          "Null": {
            "NULL": True
          },
          "String": {
            "S": "Hello"
          },
          "StringSet": {
            "SS": [
              "Giraffe",
              "Zebra"
            ]
          },
          "EmptyStringSet": {
            "SS": []
          }
        },
        "SequenceNumber": "1405400000000002063282832",
        "SizeBytes": 54,
        "StreamViewType": "NEW_AND_OLD_IMAGES"
      },
      "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/Example-Table/stream/2016-12-01T00:00:00.000"
    }
  ]
}

#
# Blank event types
#

LIST_TYPE = [
    "list1",
    "list2",
    "list3"
]

DICT_TYPE = {
    "Hello": "World!"
}

DICT_TYPE_EMPTY = {}

STR_TYPE = "string type"

INT_TYPE = 123456

FLOAT_TYPE = 123.456

NONE_TYPE = None
