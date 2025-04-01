#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

if [[ -z $FUNCS ]]; then
    echo List of FUNCS required!
    exit 1
fi

if [[ -z $URLS ]]; then
    echo Gathering URLs using aws cli
    for f in $FUNCS
    do
        URLS="$URLS $(
            aws-vault exec sso-serverless-sandbox-account-admin -- \
                aws lambda get-function-url-config \
                    --function-name $f \
                    --region sa-east-1 \
                    --output json | jq -r '.FunctionUrl'
        )"
    done
    echo Found URLs: $URLS
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
        for _ in {1..100}
        do
            (
                for _ in {1..2}
                do
                    curl "$u"
                    sleep 0.1
                done
            ) &
        done
    done
    wait
done
