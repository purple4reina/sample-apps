#!/bin/bash -e

echo "building bootstrap binary"
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bootstrap ./...
aws-vault exec sso-serverless-sandbox-account-admin -- serverless deploy
