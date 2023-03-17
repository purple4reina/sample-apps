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

    sleep 1

    for u in $URLS
    do
        curl "$u" &
    done
    wait
done
