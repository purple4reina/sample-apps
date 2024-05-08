#!/bin/bash

set -e

mkdir -p .layers/extensions/bin
GOOS=linux GOARCH=amd64 builder --config=builder-config.yml

cp start-otelcol .layers/extensions/start-otelcol
cd .layers
zip otelcol-extension.zip extensions/bin/otelcol-custom extensions/start-otelcol
cd ..

aws-vault exec sso-serverless-sandbox-account-admin -- sls deploy
