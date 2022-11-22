#!/bin/bash

# curl -L https://gist.github.com/jcstorms1/4856d7be2ae390aa923275c3806be130/raw/c49b7e2dd48d497cb4925e745efd0ca1ab8cc102/datadog-agent -o datadog-agent

if [[ -n $WITHOUT_WRAPPER ]]
then
    echo 🚫 starting without wrapper
    DOCKER_DEFAULT_PLATFORM=linux/x86_64 \
        docker run -it \
            -v $PWD:/data \
            -w /data \
            -e DD_API_KEY=$DD_API_KEY \
            -e DD_TRACE_DEBUG=true \
            -e DD_TRACE_AGENT_HOSTNAME=host.docker.internal \
            -e DD_SERVICE=rey-azure-nowrapper \
            -p 3000:3000 \
        node --require dd-trace/init bin/www
else
    echo 🎁 starting with wrapper
    DOCKER_DEFAULT_PLATFORM=linux/x86_64 \
        docker run -it \
            -v $PWD:/data \
            -v $(readlink -f $PWD/datadog_wrapper):/data/datadog_wrapper \
            -w /data \
            -e DD_RUNTIME=node \
            -e DD_API_KEY=$DD_API_KEY \
            -e DD_TRACE_DEBUG=true \
            -e DD_DIR=/data/dd \
            -e DD_BINARIES_URL="http://host.docker.internal:8000/dev" \
            -e DD_SERVICE=rey-azure-wrapper \
            -e DD_START_APP='node bin/www' \
            -p 3000:3000 \
        node bash datadog_wrapper
fi
