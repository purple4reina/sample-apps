#!/bin/bash -e

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
cd "$ROOT_DIR"/golang/old
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o ../bin/old
cd "$ROOT_DIR"/golang/new
env GOARCH=amd64 GOOS=linux go build -ldflags="-s -w" -o ../bin/new
cd "$ROOT_DIR"
