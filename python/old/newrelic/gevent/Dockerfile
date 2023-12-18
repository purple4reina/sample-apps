FROM python-base

ARG python=python3.6

ENV NEW_RELIC_CONFIG_FILE /app/newrelic.ini
ENV PYTHON $python

ADD requirements.txt /app/

RUN virtualenv /venv/env-$PYTHON --python=$PYTHON && \
    /venv/env-$PYTHON/bin/pip install -r /app/requirements.txt

ADD . /app

CMD /app/start_task.sh
