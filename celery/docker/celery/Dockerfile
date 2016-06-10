FROM python-base

RUN pip install celery newrelic django-celery django
RUN apt-get install -y curl iputils-ping less

VOLUME /data
WORKDIR /data

RUN useradd celery
RUN mkdir -p /var/log/celery
RUN chown -R celery:celery /var/log/celery
