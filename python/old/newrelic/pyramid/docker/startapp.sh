#!/bin/bash

DIR=`dirname $0`

docker-compose --file $DIR/docker-compose.yml \
    run --rm server /data/docker/start_server.sh

docker-compose --file $DIR/docker-compose.yml down
