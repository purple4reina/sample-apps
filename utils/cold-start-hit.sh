#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

if [[ -z $FUNCS ]]; then
    echo List of FUNCS required!
    exit 1
fi

if [[ -z $URLS ]]; then
    echo List of URLS required!
    exit 1
fi

while true
do
    for f in $FUNCS
    do
        "$SCRIPT_DIR/update-memory.sh" "$f" &
    done
    wait

    sleep 2

    for u in $URLS
    do
        for _ in {1..10}
        do
            (
                for _ in {1..10}
                do
                    curl "$u"
                done
            ) &
        done
    done
    wait
done
