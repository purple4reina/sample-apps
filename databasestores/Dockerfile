FROM python-base

RUN apt-get update && apt-get install curl -y

RUN pip install newrelic flask psycopg2

EXPOSE 5000
ENV NEW_RELIC_CONFIG_FILE=/data/newrelic.ini

CMD pip install -U /data/dist/* && newrelic-admin run-python /data/app.py
