#!/bin/bash -e

echo "building golang binary"
rm -rf bin
mkdir -p bin
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o bin consumer.go
echo

aws-vault exec serverless-sandbox-account-admin -- serverless deploy
