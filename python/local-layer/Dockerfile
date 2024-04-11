FROM public.ecr.aws/lambda/python:3.9

RUN yum install gcc -y

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions
CMD ["datadog_lambda.handler.handler"]

COPY handler.py .
COPY vendor/ /opt/python/

ENV DD_LAMBDA_HANDLER "handler.handle"
ENV DD_SITE "datadoghq.com"
ENV DD_ENV "local"
ENV DD_SERVICE "rey-lambda-local"
ENV DD_VERSION "0.1.0"
ENV DD_TRACE_ENABLED "true"
ENV DD_LOCAL_TEST "true"
