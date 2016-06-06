FROM python-base

RUN pip install celery newrelic django-celery django
RUN apt-get install -y curl iputils-ping less

VOLUME /data
WORKDIR /data
