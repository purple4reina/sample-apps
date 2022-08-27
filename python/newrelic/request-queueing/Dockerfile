FROM nginx

ADD nginx.conf /etc/nginx
ADD . /data/

RUN echo 'uwsgi_param HTTP_X_REQUEST_START "t=${msec}";' >> /etc/nginx/uwsgi_params

RUN apt-get update
RUN apt-get install python-pip python2.7-dev -y
RUN pip install -r /data/requirements.txt
RUN NEW_RELIC_CONFIG_FILE=/data/newrelic.ini newrelic-admin run-program uwsgi --ini /data/uwsgi.ini
