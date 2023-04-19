#!/bin/bash -e

ROOT_DIR=$(git rev-parse --show-toplevel)/apps/otlp
ARTIFACTS_DIR="$ROOT_DIR/.artifacts"
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# golang
GOARCH=amd64 GOOS=linux go build -o "$ARTIFACTS_DIR/handler" golang/handler.go
zip -j "$ARTIFACTS_DIR/golang.zip" "$ARTIFACTS_DIR/handler"

# java
cd "$ROOT_DIR/java"
./gradlew clean build
filename=rey-app-otlp-dev-java-dev-all.jar
cp "build/libs/$filename" "$ARTIFACTS_DIR/java.jar"
rm -rf build
cd "$ROOT_DIR"

# node
cd "$ROOT_DIR/node"
npm install
zip -qr "$ARTIFACTS_DIR/node.zip" handler.js instrument.js node_modules
cd "$ROOT_DIR"

# python
zip -j "$ARTIFACTS_DIR/python.zip" python/handler.py

# deploy
aws-vault exec serverless-sandbox-account-admin -- sls deploy
