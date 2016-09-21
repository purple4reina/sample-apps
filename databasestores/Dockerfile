FROM python-base

RUN apt-get update
RUN apt-get install -y postgresql curl

# start postgres
ADD postgresql.conf /etc/postgresql/9.1/main/
USER postgres
RUN /etc/init.d/postgresql start && \
    /usr/bin/psql --command "CREATE USER root with SUPERUSER PASSWORD 'root';" && \
    /usr/bin/createdb -O root root

# run the app
ENV NEW_RELIC_CONFIG_FILE=/data/newrelic.ini
