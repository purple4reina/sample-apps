#!/bin/bash -e

# Use this script to build binaries and gather dependencies before deploying.
# Not required for configuration changes, but is required if Java or Golang
# code changes.

ROOT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

echo "building java binary"
cd "$ROOT_DIR"/java
rm -rf bin build
docker run -it --rm \
    --platform linux/amd64 \
    -v "$PWD":/java \
    -w /java \
        amd64/gradle gradle build
cd "$ROOT_DIR"
echo

echo "building golang binary"
cd "$ROOT_DIR"/golang
rm -rf bin
mkdir -p bin
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o client/bootstrap client/client.go
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o server/bootstrap server/server.go
cd "$ROOT_DIR"
echo

echo "packaging python dependencies"
cd "$ROOT_DIR"
rm -rf env
mkdir -p env/python
cd env/python
pip install -r "$ROOT_DIR"/requirements.txt -t .
zip -r requirements-layer.zip .
cd "$ROOT_DIR"
echo
