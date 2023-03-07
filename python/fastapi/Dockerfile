FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init

ENV DD_SERVICE=rey-fastapi-test
ENV DD_ENV=dev
ENV DD_VERSION=1

ENTRYPOINT ["/app/datadog-init"]
CMD uvicorn --port $PORT --host 0.0.0.0 main:app
