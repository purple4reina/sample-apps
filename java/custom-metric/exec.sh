#!/bin/bash

while true
do
    for _ in {1..50}
    do
        curl https://oqrarzliowcus6dy6gztyazxc40bkkbf.lambda-url.sa-east-1.on.aws &
        sleep 10
        curl https://oqrarzliowcus6dy6gztyazxc40bkkbf.lambda-url.sa-east-1.on.aws &
    done &

    sleep 600
done
