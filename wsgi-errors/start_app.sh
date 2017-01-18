#!/bin/bash

function usage {
    echo "./start_app.sh <wsgi-type>"
    echo "    where <wsgi-type> is either \"uwsgi\" or \"gunicorn\""
    exit 1
}

WSGI=$1
test $WSGI && ([[ $WSGI == gunicorn ]] || [[ $WSGI == uwsgi ]]) || usage

if [[ -f env/bin/activate ]]
then
    source env/bin/activate
    pip install -r requirements.txt
else
    virtualenv env
    source env/bin/activate
    pip install -r requirements
fi

if [[ $WSGI == gunicorn ]]
then
    newrelic-admin run-program gunicorn app:application
elif [[ $WSGI == uwsgi ]]
then
    newrelic-admin run-program uwsgi \
        --http :8000 \
        --wsgi app:application \
        --single-interpreter \
        --enable-threads
fi
