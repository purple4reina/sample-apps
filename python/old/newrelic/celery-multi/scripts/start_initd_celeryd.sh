#!/bin/bash -e


app=$1
if [[ -n app ]] ; then
    # backward compatability
    app=tasks
fi

CELERY_APP=$app ./init.d/celeryd start
tail -f /var/log/celery/*.log
