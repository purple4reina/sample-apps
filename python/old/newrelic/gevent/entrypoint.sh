#!/bin/bash -e

pip install -e /agent

/venv/env-$PYTHON/bin/python /app/task.py
