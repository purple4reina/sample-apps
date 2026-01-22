FROM python

WORKDIR /app
COPY app.py requirements.txt ./
RUN pip install -r requirements.txt

ENV DD_SERVICE=rey-python-cloudrun
ENV DD_ENV=rey
ENV DD_VERSION=1
ENV DD_TRACE_ENABLED=true
ENV DD_REMOTE_CONFIGURATION_ENABLED=false

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init

ENTRYPOINT ["/app/datadog-init"]
CMD ddtrace-run gunicorn -w 4 app:app
