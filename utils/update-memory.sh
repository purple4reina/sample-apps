#!/bin/bash

funcname=$1

aws-vault exec serverless-sandbox-account-admin -- aws lambda update-function-configuration \
    --function "arn:aws:lambda:sa-east-1:425362996713:function:$funcname" \
    --region sa-east-1 \
    --memory-size $(( RANDOM % 1024 + 128 ))
