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
