FROM python-base

ADD requirements.txt /data/requirements.txt
RUN virtualenv /env --python=python2.7 && \
    /env/bin/pip install -r /data/requirements.txt
