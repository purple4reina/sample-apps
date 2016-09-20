FROM python-base

RUN apt-get update
RUN apt-get install curl -y

ADD requirements.txt app.py newrelic.ini /app/
RUN pip install -r /app/requirements.txt

ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini
EXPOSE 5000

CMD newrelic-admin run-python /app/app.py
