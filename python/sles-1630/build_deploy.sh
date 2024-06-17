#!/bin/bash

echo "Downloading aws_lambda_powertools 📦"
rm -rf vendor aws_lambda_powertools
pip install -t vendor aws_lambda_powertools
mv vendor/aws_lambda_powertools .
rm -rf vendor

echo
echo "Deploying serverless stack 🚀"
aws-vault exec sso-serverless-sandbox-account-admin -- \
    serverless deploy
