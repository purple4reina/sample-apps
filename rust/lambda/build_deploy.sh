#!/bin/bash

echo "Building 🏗️"
cargo lambda build --release

echo "Deploying 🚀"
aws-vault exec sso-serverless-sandbox-account-admin -- \
  cargo lambda deploy --region sa-east-1
