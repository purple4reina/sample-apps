#!/bin/bash -e

echo "📦 packaging release"
rm -rf bin bootstrap
CGO_ENABLED=0 GOARCH=amd64 GOOS=linux go build -o bootstrap handler.go
echo -n "🚀 deploying package"
aws-vault exec sso-serverless-sandbox-account-admin -- sls deploy
echo
echo "🎉 deploy complete at $(date)"
