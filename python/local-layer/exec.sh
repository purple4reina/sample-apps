#!/bin/bash

set -e

DEPS_DIR=vendor

rm -rf $DEPS_DIR
mkdir -p $DEPS_DIR

pip3.9 install \
    -r requirements.txt \
    -t $DEPS_DIR \
    --platform=manylinux2014_x86_64 --only-binary=:all: \
    --no-cache-dir

docker build -t localtest --platform=linux/amd64 .

docker_id=$(
    docker run -d \
        --platform=linux/amd64 \
        -p 9000:8080 \
        -e DD_API_KEY="$DD_API_KEY" \
            localtest
)
trap 'docker stop $docker_id ; docker logs $docker_id' EXIT

sleep 0.5
date
curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'

echo ; echo
