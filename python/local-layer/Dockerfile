FROM public.ecr.aws/lambda/python:3.9

RUN yum install gcc -y

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions
CMD ["datadog_lambda.handler.handler"]

COPY handler.py .

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt -t /opt/python

COPY .layer /layer
RUN python3 -m pip install /layer/datadog-lambda-python -t /opt/python

ENV DD_LAMBDA_HANDLER "handler.handle"
ENV DD_API_KEY "YOUR_API_KEY"
ENV DD_SITE "datadoghq.com"
ENV DD_ENV "local"
ENV DD_SERVICE "rey-lambda-local"
ENV DD_VERSION "0.1.0"
ENV DD_TRACE_ENABLED "true"
ENV DD_LOCAL_TEST "true"
ENV DD_COLD_START_TRACING "true"
ENV DD_COLD_START_TRACE_SKIP_LIB "datadog_lambda.handler,importlib.metadata,requests"
#ENV DD_MIN_COLD_START_DURATION "0"
#ENV DD_TRACE_DEBUG "true"
#ENV DD_TRACE_PARTIAL_FLUSH_ENABLED "1"
#ENV DD_TRACE_PARTIAL_FLUSH_MIN_SPANS "1"
