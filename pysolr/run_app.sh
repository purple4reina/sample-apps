#!/bin/bash

virtualenv env
source env/bin/activate
pip install pysolr newrelic

python app.py
