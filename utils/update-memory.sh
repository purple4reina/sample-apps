#!/bin/bash

funcname=$1

if [[ -z $REGION ]]; then
    REGION=sa-east-1
fi
if [[ -z $ACCOUNT ]]; then
    ACCOUNT=425362996713
fi

aws-vault exec sso-serverless-sandbox-account-admin -- aws lambda update-function-configuration \
    --function "arn:aws:lambda:$REGION:$ACCOUNT:function:$funcname" \
    --region $REGION \
    --memory-size $(( RANDOM % 64 + 1024 )) \
    --query MemorySize
