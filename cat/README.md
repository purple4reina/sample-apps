# Cross Application Tracing

This application illustrates cross application tracing (CAT)

Run app one `NEW_RELIC_CONFIG_FILE=newrelic-web.ini newrelic-admin run-python app1.py`

Run app two `NEW_RELIC_CONFIG_FILE=newrelic-api.ini newrelic-admin run-python app2.py`

Send it traffic `while true ; do curl http://localhost:5000 ; sleep 1 ; done`
