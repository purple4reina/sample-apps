#!/bin/bash -e

ROOT_DIR=$(git rev-parse --show-toplevel)/apps/otlp
ARTIFACTS_DIR="$ROOT_DIR/.artifacts"
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# golang
echo "🏌 Building golang"
GOARCH=amd64 GOOS=linux go build -o "$ARTIFACTS_DIR/handler" golang/handler.go
zip -j "$ARTIFACTS_DIR/golang.zip" "$ARTIFACTS_DIR/handler"

# node
echo "💠 Building node"
cd "$ROOT_DIR/node"
npm install
zip -qr "$ARTIFACTS_DIR/node.zip" handler.js instrument.js node_modules
cd "$ROOT_DIR"

# python
echo "🐍 Building python"
zip -j "$ARTIFACTS_DIR/python.zip" python/handler.py

# deploy
echo "🚀 Deploying"
aws-vault exec serverless-sandbox-account-admin -- sls deploy
