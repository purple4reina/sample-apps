#!/bin/bash -e

ROOT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

echo "building java binary"
cd "$ROOT_DIR"/java
JAVA_HOME=$JAVA_11_HOME gradle build
cd "$ROOT_DIR"

aws-vault exec serverless-sandbox-account-admin -- serverless deploy
