FROM public.ecr.aws/lambda/python:latest

COPY --from=public.ecr.aws/datadog/lambda-extension:58 /opt/extensions/ /opt/extensions
ENV DD_LAMBDA_HANDLER handler.handler
CMD ["datadog_lambda.handler.handler"]

RUN pip install aws_lambda_powertools ddtrace datadog-lambda

ENV DD_ENV=dev
ENV DD_SERVICE=rey-sles-1630
ENV DD_VERSION=1
ENV DD_TRACE_DEBUG=true
ENV DD_TRACE_ENABLED=true

COPY handler.py my_logging.py .
