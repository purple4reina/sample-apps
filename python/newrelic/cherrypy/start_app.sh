#!/bin/bash

UWSGI='../../external_packages/uwsgi/uwsgi'
BEHAVIOR=cheat

echo "Using behavior $BEHAVIOR"

ARGS="
    --socket 127.0.0.1:8080
    --protocol http
    --wsgi-file app.py
    --callable wsgiapp
    --enable-threads
    --single-interpreter
    --honour-stdin
    --wsgi-env-behavior $BEHAVIOR
"

if [[ -n $WITH_GDB ]]
then
    CMD="gdb --args $UWSGI $ARGS"
else
    CMD="$UWSGI $ARGS"
fi

echo $CMD
exec $CMD
