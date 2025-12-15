#!/bin/bash

funcname=$1

if [[ -z $REGION ]]; then
    REGION=sa-east-1
fi
if [[ -z $ACCOUNT ]]; then
    ACCOUNT=425362996713
fi

memsize=$(
    aws-vault exec sso-serverless-sandbox-account-admin -- aws lambda get-function-configuration \
        --function-name "$funcname" \
        --region $REGION \
        --query MemorySize
)
if [ $(( memsize % 2 )) = 0 ]; then
    memsize=$(( memsize + 1 ))
else
    memsize=$(( memsize - 1 ))
fi

aws-vault exec sso-serverless-sandbox-account-admin -- aws lambda update-function-configuration \
    --function "arn:aws:lambda:$REGION:$ACCOUNT:function:$funcname" \
    --region $REGION \
    --memory-size $memsize \
    --query MemorySize
