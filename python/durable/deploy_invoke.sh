#!/bin/bash -e

rm -f outfile.json

export AWS_REGION=us-east-2

aws-vault exec sso-serverless-sandbox-account-admin -- \
    cdk deploy --toolkit-stack-name ReyCDKToolkit --qualifier reycdk \
        --context @aws-cdk/core:bootstrapQualifier=reycdk

aws-vault exec sso-serverless-sandbox-account-admin -- \
    aws lambda invoke \
        --region $AWS_REGION \
        --function-name='arn:aws:lambda:us-east-2:425362996713:function:rey-durable-function:$LATEST' \
        --payload=$(echo '{"hello":"world"}' | base64) \
    outfile.json

cat outfile.json | jq
