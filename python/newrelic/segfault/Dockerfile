FROM python:2.7.15
#FROM python:3.6.6

WORKDIR /data

RUN pip install uwsgi==2.0.17.1

CMD uwsgi \
    --http :8000 \
    --wsgi app:application \
    --max-requests 3 \
    --min-worker-lifetime 0 \
    --master

ADD app.py /data
