#!/bin/bash -e

echo "📦 packaging release"
rm -rf bin
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bin/handler handler.go
echo
echo "🚀 deploying package"
aws-vault exec serverless-sandbox-account-admin -- sls deploy --force
echo
echo "🎉 deploy complete at $(date)"
