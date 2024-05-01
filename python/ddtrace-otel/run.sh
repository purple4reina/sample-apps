#!/bin/bash


export DD_TRACE_OTEL_ENABLED=true
export DD_SERVICE=rey-ddtrace-otel
export DD_ENV=rey

ddtrace-run python app.py
