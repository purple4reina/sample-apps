#!/bin/bash

set -e

rm -rf .layer
rsync -ax \
    --exclude .git \
    --exclude env \
    --exclude tests \
    --exclude __pycache__ \
    --exclude .github \
    --exclude .layers \
    --exclude scripts \
    --exclude .DS_Store \
    --exclude .gitignore \
    --exclude .pytest_cache \
    --exclude dist \
    --exclude .vscode \
        ../../../datadog-lambda-python .layer

docker build -t localtest .
docker_id=$(docker run -d -p 9000:8080 localtest)
trap 'docker stop $docker_id ; docker logs $docker_id' EXIT

sleep 0.5
curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'

rm -rf .layer .tracer
