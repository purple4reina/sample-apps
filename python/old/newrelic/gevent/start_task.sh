#!/bin/bash -e

/venv/env-$PYTHON/bin/pip install -e /agent >/dev/null

/venv/env-$PYTHON/bin/python /app/task.py
