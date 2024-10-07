#!/bin/bash

URL="https://w24vb5kyh5kgc4a7lpscufuy5i0xkrmd.lambda-url.sa-east-1.on.aws"

while true
do
    for _ in {1..50}
    do
        (
            curl $URL &
            sleep 10
            curl $URL &
        ) &
    done &

    sleep 600
    echo ; echo
done
