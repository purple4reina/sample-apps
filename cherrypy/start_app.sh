#!/bin/bash

ARGS='
    --socket 127.0.0.1:8080
    --protocol http
    --wsgi-file app.py
    --callable wsgiapp
    --enable-threads
    --single-interpreter
    --wsgi-env-behavior holy
    --honour-stdin
'

if [[ -n $WITH_GDB ]]
then
    CMD="gdb --args env/bin/uwsgi $ARGS"
else
    CMD="env/bin/uwsgi $ARGS"
fi

echo $CMD
exec $CMD
