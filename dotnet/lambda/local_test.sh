#!/bin/bash

dotnet build

dotnet lambda package \
    --configuration Release \
    --package-type image \
    --image-tag dotnet/lambda-local-test

rm -rf logs
mkdir -p logs

dockerId=$(
    docker run -d \
        -v $PWD/logs:/var/log/datadog/dotnet \
        -p 9000:8080 \
        dotnet/lambda-local-test
)

echo ; echo "waiting..."
sleep 1
echo "running dotnet lambda function"
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{"payload":"hello world!"}'

echo ; echo ; echo "stopping docker image"
docker stop $dockerId

echo ; echo "docker logs output:"
docker logs $dockerId

echo ; echo "tracer debug logs content:"
cat logs/*
