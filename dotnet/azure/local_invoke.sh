#!/bin/bash

function _print_yellow {
    args=$@
    echo -e $(printf "\e[33m${args}\e[0m")
}

rm -rf published

dotnet publish \
    -c Release \
    -o published \
    MyFirstAzureWebApp

if [[ -n $WITHOUT_WRAPPER ]]
then
    _print_yellow 🚫 starting without wrapper
    dotnet published/MyFirstAzureWebApp.dll --urls http://localhost:7000
else
    LOG_DIR=dd/var/log

    rm -rf dd

    _print_yellow 🎁 starting with wrapper
    dockerId=$(docker run -d \
            --platform linux/x86_64 \
            -v $PWD:/data \
            -v $(readlink -f $PWD/datadog_wrapper):/data/datadog_wrapper \
            -w /data \
            -e DD_API_KEY=$DD_API_KEY \
            -e DD_BINARIES_URL="http://host.docker.internal:8000/dev" \
            -e DD_DIR=/data/dd \
            -e DD_RUNTIME=dotnet \
            -e DD_SERVICE=rey-dotnet-wrapper \
            -e DD_START_APP='dotnet published/MyFirstAzureWebApp.dll --urls http://localhost:7000' \
            -e DD_TRACE_DEBUG=true \
            -e DD_TRACE_LOG_DIRECTORY=/data/$LOG_DIR \
            -p 7000:7000 \
            mcr.microsoft.com/dotnet/sdk:6.0 \
        bash datadog_wrapper)
    _print_yellow "started docker container $dockerId"

    _print_yellow "tailing logs"
    docker logs -f $dockerId &

    _print_yellow "sleeping........"
    sleep 30

    echo "while true ; do curl http://localhost:7000 & sleep 1 ; done" > run.sh
    docker exec $dockerId bash /data/run.sh &

    _print_yellow "sleeping........"
    sleep 10

    _print_yellow "tailing tracer logs"
    tail -f $LOG_DIR/*

    _print_yellow "stopping app"
    docker stop $dockerId
fi
