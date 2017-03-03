#!/bin/bash

function usage() {
    echo "Usage: start_app.sh OPTIONS"
    echo "  Required options:"
    echo "      -s|--server         Which wsgi server to use:"
    echo "                              uwsgi, mod-wsgi, gunicorn"
    echo "      -a|--app|--application"
    echo "                          Application to run, in the form of"
    echo "                              file:object"
    echo "      -n|--newrelic       Use the agent"
    echo "      -d|--disable-browser"
    echo "                          Disable browser monitoring"
    echo "      -p|--port           Port to serve the app on"

    exit 1
}

while test "$#" -ne 0
do
    case $1 in
        -s|--server)
            shift
            SERVER=$1
            shift
            ;;
        -a|--app|--application)
            shift
            APP=$1
            shift
            ;;
        -p|--port)
            shift
            PORT=$1
            shift
            ;;
        -n|--newrelic)
            USE_AGENT=true
            shift
            ;;
        -b|--disable-browser)
            DISABLE_BROWSER=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [[ -z $APP ]]
then
    usage
fi

if [[ -z $PORT ]]
then
    usage
fi

if [[ $SERVER == 'uwsgi' ]]
then
    CMD="uwsgi --socket 127.0.0.1:$PORT --protocol http --wsgi $APP --enable-threads --single-interpreter --wsgi-env-behavior holy"

    if [[ $USE_AGENT == true ]]
    then
        echo 'Using python agent...'
        export USE_AGENT=true
        export PYTHONPATH=$PYAGENT_DIR:$PYTHONPATH
    fi

elif [[ $SERVER == 'mod-wsgi' ]]
then
    echo mod-wsgi
elif [[ $SERVER == 'gunicorn' ]]
then
    CMD="gunicorn $APP --log-level DEBUG --bind 127.0.0.1:$PORT"

    if [[ $USE_AGENT == true ]]
    then
        echo 'Using python agent...'
        CMD="newrelic-admin run-program $CMD"
    fi

else
    usage
fi

if [[ $DISABLE_BROWSER == true ]]
then
    echo 'Disabling browser monitoring...'
    export NEW_RELIC_CONFIG_FILE=newrelic-nobrowser.ini
else
    export NEW_RELIC_CONFIG_FILE=newrelic.ini
fi

export NEW_RELIC_APP_NAME="$SERVER-$APP-${DISABLE_BROWSER:-false}-$PORT"

git_branch="$(cd $PYAGENT_DIR ; git branch | grep \* | cut -d ' ' -f2)"
git_describe="$(cd $PYAGENT_DIR ; git rev-parse HEAD)"
export GIT_SHA="${git_branch} (${git_describe})"
echo "Using transaction names: $GIT_SHA"

echo "Running command:  $CMD"
exec $CMD
