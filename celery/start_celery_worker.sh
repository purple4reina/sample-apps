#!/bin/bash

NEW_RELIC_CONFIG_FILE=worker-newrelic.ini newrelic-admin run-program celery worker -A tasks --concurrency=1 -l info
