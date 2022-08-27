FROM python-base

ADD requirements.txt /data/

RUN pip install --upgrade pip
RUN pip install -r /data/requirements.txt

EXPOSE 8000

WORKDIR /data

ADD * /data/
