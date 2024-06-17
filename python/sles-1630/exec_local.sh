#!/bin/bash -e

echo "Building the docker image 🧱"
docker build -t localtest . 2>&1

echo
echo "Running the docker container 🏃"
docker_id=$(
    docker run -d \
        -p 9000:8080 \
        -e DD_API_KEY="$DD_API_KEY" \
            localtest
)
trap 'docker stop $docker_id ; docker logs $docker_id 2>&1' EXIT

sleep 1
echo
echo "Executing function locally 🚀"
date
curl http://localhost:9000/2015-03-31/functions/function/invocations -d '{}' 2>&1 &
sleep 1

echo
echo "Logs from the container 📜"
