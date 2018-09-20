FROM python:2.7.15

ADD requirements.txt /
RUN pip install -r /requirements.txt

ENV NEW_RELIC_CONFIG_FILE /data/newrelic.ini
WORKDIR /data
EXPOSE 8000

CMD newrelic-admin run-program uwsgi \
    --http :8000 \
    --wsgi app:application \
    --enable-threads \
    --single-interpreter \
    --max-requests 3 \
    --min-worker-lifetime 0 \
    --master

ADD . /data
