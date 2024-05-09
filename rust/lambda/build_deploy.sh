#!/bin/bash

echo "Building 🏗️"
rm -rf target/
cargo lambda build --release -o zip

echo "Deploying 🚀"
aws-vault exec sso-serverless-sandbox-account-admin -- \
    sls deploy
