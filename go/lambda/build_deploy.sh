#!/bin/bash -e

echo "📦 packaging release"
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bin/handler handler.go
echo
echo "🚀 deploying package"
sls deploy --force
echo
echo "🎉 deploy complete at $(date)"
