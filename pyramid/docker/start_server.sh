#!/bin/bash

cd /data/MyProject

pip install -e . > /dev/null

newrelic-admin run-program pserve development.ini
