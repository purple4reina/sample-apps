#!/bin/bash

URL="https://xyph7nwykrb3ce26f2fuzdtxby0xdzot.lambda-url.sa-east-1.on.aws"
FUNC="rey-java-custom-metric-dev-simple"

while true
do
    date
    for _ in {1..50}
    do
        (
            curl $URL &
            sleep 10
            curl $URL &
        ) &
    done &

    sleep 60

    num=$(./test.sh)
    echo -n " $num"
    if [ $((num % 100)) -ne 0 ]
    then
        echo -n " stopping"
        ../../utils/update-memory.sh $FUNC
    fi

    echo ; echo
done
