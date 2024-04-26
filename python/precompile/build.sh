#!/bin/bash

set -ex

export DOCKER_DEFAULT_PLATFORM=linux/amd64
dockerid=$(docker run -d python:3.12 sleep 1000)
trap "docker rm -vf $dockerid" EXIT

docker exec $dockerid pip install -t /vendor numpy
docker exec $dockerid find /vendor -name 'tests' -type d -exec rm -rf {} +
docker exec $dockerid find /vendor -name '__pycache__' -type d -exec rm -rf {} +
docker exec $dockerid python -m compileall -b /vendor

rm -rf vendor bin numpy*
docker cp $dockerid:/vendor/ .

mv vendor/* .
rm -rf vendor *.dist-info bin
