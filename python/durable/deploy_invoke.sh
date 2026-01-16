#!/bin/bash

rm -f outfile.json

aws-vault exec sso-serverless-sandbox-account-admin -- \
    cdk deploy

aws-vault exec sso-serverless-sandbox-account-admin -- \
    aws lambda invoke \
        --function-name='arn:aws:lambda:us-east-1:425362996713:function:rey-durable-function:$LATEST' \
        --payload=$(echo '{"hello":"world"}' | base64) \
    outfile.json

cat outfile.json | jq
