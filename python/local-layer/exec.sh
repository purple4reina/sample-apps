#!/bin/bash

set -e

DEPS_DIR=vendor
TRACER_DIR=.tracer

rm -rf $DEPS_DIR $TRACER_DIR
mkdir -p $DEPS_DIR

pip3.9 install \
    -r requirements.txt \
    -t $DEPS_DIR \
    --platform=manylinux2014_aarch64 --only-binary=:all: \
    --no-deps \
    --no-cache-dir

cp -r "$DD_DIR"/dd-trace-py/ $TRACER_DIR

docker build -t localtest .

docker_id=$(
    docker run -d \
        -p 9000:8080 \
        -e DD_API_KEY="$DD_API_KEY" \
            localtest
)
trap 'docker stop $docker_id ; docker logs $docker_id' EXIT

sleep 0.5
date
curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'

echo ; echo
