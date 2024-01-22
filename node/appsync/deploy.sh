#!/bin/bash -e

ROOT_DIR=$(git rev-parse --show-toplevel)/node/appsync

cd $ROOT_DIR
rm -rf dist
mkdir dist

cd $ROOT_DIR/Lambdas
rm -rf node_modules
npm install
zip -q -r $ROOT_DIR/dist/blog.zip *

cd $ROOT_DIR

aws-vault exec sso-serverless-sandbox-account-admin -- serverless deploy
