#!/bin/bash

if [[ -f env/bin/activate ]]
then
    source env/bin/activate
    pip install -r requirements.txt
else
    virtualenv env
    source env/bin/activate
    pip install -r requirements
fi

newrelic-admin run-program gunicorn app:application
