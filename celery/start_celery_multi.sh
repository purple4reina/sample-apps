#!/bin/bash -e


app=$1
if [[ -n app ]] ; then
    # backward compatability
    app=tasks
fi

rm multi-audit.log *.pid || true
NEW_RELIC_CONFIG_FILE=multi-newrelic.ini newrelic-admin run-program \
    celery multi start node1 -A $app --concurrency=1 -l info
tail -f node1.log
