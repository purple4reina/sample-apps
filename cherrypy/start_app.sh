#!/bin/bash

newrelic-admin run-program uwsgi \
    --socket 127.0.0.1:8080 \
    --protocol=http \
    --wsgi-file app.py \
    --callable wsgiapp \
    --enable-threads \
    --single-interpreter \
    --wsgi-env-behavior=holy
