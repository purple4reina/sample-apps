#!/bin/bash -e

echo "🏗  pip installing datadog_agent package"
pip install ~/dd/datadog-agent-from-code-python

echo "🚀 executing script in docker"

docker run -it \
    -v $PWD:/data \
    -e DD_API_KEY=$DD_API_KEY \
    -e DD_ENV=dev \
    -e DD_LOG_LEVEL=debug \
    -e DD_SERVICE=rey-hack-a-dog \
    -e DD_TRACE_DEBUG=true \
    -e DD_TRACE_LOG_FILE=/var/log/datadog.log \
    -e DD_TAGS=rey:true \
    -e PYTHONPATH=/data/env/lib/python3.9/site-packages \
python bash -c 'pip install ddtrace && /data/app.py'

echo "🎉 done!"
