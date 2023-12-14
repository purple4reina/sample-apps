#!/bin/bash

funcname=$1

if [[ -z $REGION ]]; then
    REGION=sa-east-1
fi

aws-vault exec sso-serverless-sandbox-account-admin -- aws lambda update-function-configuration \
    --function "arn:aws:lambda:$REGION:425362996713:function:$funcname" \
    --region $REGION \
    --memory-size $(( RANDOM % 1024 + 128 )) | jq '.MemorySize'
