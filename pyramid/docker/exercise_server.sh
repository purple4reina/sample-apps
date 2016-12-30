#!/bin/bash

url=http://localhost:6543/mongo

while true
do
    sleep 1
    docker exec -it docker_server_run_1 curl $url
done
