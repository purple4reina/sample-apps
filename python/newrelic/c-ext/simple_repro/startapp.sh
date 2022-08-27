#!/bin/bash

uwsgi --http :8000 \
    -H env \
    --wsgi-file application.py \
    --fs-reload application.py \
    &

while true
do
    curl http://localhost:8000 > /dev/null 2>&1
    sleep 1
done
