#!/bin/bash -e

echo "📦 packaging release"
rm -rf bin
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bootstrap handler.go
echo
echo "🚀 deploying package"
aws-vault exec sso-serverless-sandbox-account-admin -- sls deploy
echo
echo "🎉 deploy complete at $(date)"
