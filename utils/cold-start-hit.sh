#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

if [[ -z $FUNCS ]]; then
    echo List of FUNCS required!
    exit 1
fi

if [[ -z $FORCE_COLD_START ]]; then
    FORCE_COLD_START="true"
fi

for f in $FUNCS
do
    (
        URL="$(
        aws-vault exec sso-serverless-sandbox-account-admin -- \
            aws lambda get-function-url-config \
                --function-name "$f" \
                --region sa-east-1 \
                --output json | jq -r '.FunctionUrl'
        )"
        echo "Found URL: $URL"

        while true
        do
            if [[ $FORCE_COLD_START = "true" ]]
            then
                "$SCRIPT_DIR/update-memory.sh" "$f" &
                sleep 2
            fi

            for _ in {1..2}
            do
                (
                    for _ in {1..200}
                    do
                        curl "$URL"
                        sleep 0.1
                    done
                ) &
            done
            wait
        done
    ) &
done
wait
