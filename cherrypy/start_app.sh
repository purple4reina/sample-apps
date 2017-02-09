#!/bin/bash

env/bin/newrelic-admin run-program env/bin/uwsgi \
    --socket 127.0.0.1:8080 \
    --protocol http \
    --wsgi-file app.py \
    --callable wsgiapp \
    --enable-threads \
    --single-interpreter \
    --wsgi-env-behavior holy
