FROM python:2.7.15

ENV NEW_RELIC_CONFIG_FILE /data/newrelic.ini
WORKDIR /data
EXPOSE 8000

RUN pip install uwsgi==2.0.17.1

CMD newrelic-admin run-program uwsgi \
    --http :8000 \
    --wsgi app:application \
    --enable-threads \
    --single-interpreter \
    --max-requests 3 \
    --min-worker-lifetime 0 \
    --master

ADD . /data
RUN pip install /data/newrelic-4.5.0.0.tar.gz
