#!/bin/bash

if [[ -z $FUNCS ]]; then
    FUNCS="
    "
fi

if [[ -z $URLS ]]; then
    URLS="
    "
fi

while true
do
    for f in $FUNCS
    do
        ./update-memory.sh "$f" &
    done
    wait

    sleep 1

    for u in $URLS
    do
        curl "$u" &
    done
    wait
done
