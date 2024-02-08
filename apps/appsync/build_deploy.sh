#!/bin/bash -e

echo "📦 packaging release"
rm -rf bin
cd client
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o ../bin/handler main.go
cd ..
echo
echo "🚀 deploying package"
aws-vault exec sso-serverless-sandbox-account-admin -- sls deploy
echo
echo "🎉 deploy complete at $(date)"
