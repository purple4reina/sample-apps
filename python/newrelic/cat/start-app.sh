#!/bin/bash

NEW_RELIC_CONFIG_FILE=newrelic-app1.ini newrelic-admin run-python app1.py &
NEW_RELIC_CONFIG_FILE=newrelic-app2.ini newrelic-admin run-python app2.py &
NEW_RELIC_CONFIG_FILE=newrelic-app3.ini newrelic-admin run-python app3.py &
