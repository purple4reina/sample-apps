#!/bin/bash

while true
do
    for _ in {1..50}
    do
        (
            curl https://kayyvs6owqwxmekjpi4kwuimyu0fctcj.lambda-url.sa-east-1.on.aws &
            sleep 10
            curl https://kayyvs6owqwxmekjpi4kwuimyu0fctcj.lambda-url.sa-east-1.on.aws &
        ) &
    done &

    sleep 600
    echo ; echo
done
