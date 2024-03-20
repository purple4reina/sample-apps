#!/bin/bash

set -e

rm -rf .layer
rsync -ax \
    --exclude .git \
    --exclude .github \
    --exclude .layers \
    --exclude scripts \
    --exclude .DS_Store \
    --exclude .gitignore \
    --exclude .vscode \
        ../../../datadog-lambda-go .layer

docker build -t localtest .
docker_id=$(docker run -d \
    -p 9000:8080 \
    --entrypoint \
    /usr/local/bin/aws-lambda-rie localtest)
trap "docker stop $docker_id ; docker logs $docker_id | grep -v 'DATADOG TRACER CONFIGURATION'" EXIT

sleep 0.5
echo
date
curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'
echo

rm -rf .layer
