FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y wget apt-transport-https curl python-pip net-tools && \
    pip install -U pip newrelic

ADD unit.list /etc/apt/sources.list.d/

RUN wget -O /root/nginx_signing.key \
        https://nginx.org/keys/nginx_signing.key?_ga=3.184489891.409074069.1520036691-1706610070.1520036691 && \
    apt-key add /root/nginx_signing.key && \
    apt-get update && \
    apt-get install -y unit unit-python2.7

EXPOSE 8400
ENV NEW_RELIC_LICENSE_KEY=f429aaa8f9c1687093c9bd211ef189b75952bf42
ENV NEW_RELIC_APP_NAME='Nginx Unit'
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_LOG_LEVEL=DEBUG
ENV NEW_RELIC_ENABLED=true

ADD wsgi.py /usr/share/doc/unit-python2.7/examples/python-app

CMD ["/usr/sbin/unitd", "--no-daemon", "--control", "unix:/var/run/control.unit.sock", "--log", "/dev/stdout"]
