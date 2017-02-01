FROM python-base

ARG python=python3.6

ENV NEW_RELIC_CONFIG_FILE /app/newrelic.ini
ENV PYTHON $python

ADD . /app

RUN virtualenv /venv/env-$PYTHON --python=$PYTHON && \
    /venv/env-$PYTHON/bin/pip install -r /app/requirements.txt

CMD /venv/env-$PYTHON/bin/newrelic-admin run-program /venv/env-$PYTHON/bin/python /app/app.py
