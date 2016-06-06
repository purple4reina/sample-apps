#!/bin/bash -e


app=$1
if [[ -n app ]] ; then
    # backward compatability
    app=tasks
fi

rm multi-audit.log node1.log *.pid || true
cd django_app/myproject
NEW_RELIC_CONFIG_FILE=multi-newrelic.ini newrelic-admin run-program \
    ./manage.py \
    celery multi start node1 -A $app --concurrency=1 -l info
tail -f -n 100 node1.log
