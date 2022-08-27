#!/bin/bash

# launch servers
./start_app.sh --newrelic --server gunicorn --app app:app_list --port 8000 &
./start_app.sh --newrelic --server gunicorn --app app:app_list --disable-browser --port 8001 &

./start_app.sh --newrelic --server gunicorn --app app:app_iter --port 8002 &
./start_app.sh --newrelic --server gunicorn --app app:app_iter --disable-browser --port 8003 &

./start_app.sh --newrelic --server gunicorn --app app:app_str --port 8004 &
./start_app.sh --newrelic --server gunicorn --app app:app_str --disable-browser --port 8005 &

./start_app.sh --newrelic --server gunicorn --app app:app_list_exc_1 --port 8006 &
./start_app.sh --newrelic --server gunicorn --app app:app_list_exc_1 --disable-browser --port 8007 &

./start_app.sh --newrelic --server gunicorn --app app:app_list_exc_2 --port 8008 &
./start_app.sh --newrelic --server gunicorn --app app:app_list_exc_2 --disable-browser --port 8009 &

./start_app.sh --newrelic --server gunicorn --app app:app_iter_exc_1 --port 8010 &
./start_app.sh --newrelic --server gunicorn --app app:app_iter_exc_1 --disable-browser --port 8011 &

# launch curlers
while true
do
    sleep 1

    for port in {8000..8011}
    do
        curl http://localhost:${port} &
    done

done
