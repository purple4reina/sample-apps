FROM public.ecr.aws/lambda/python:latest

COPY --from=public.ecr.aws/datadog/lambda-extension:latest /opt/. /opt/
ENV DD_LAMBDA_HANDLER handler.handle
CMD ["datadog_lambda.handler.handler"]

RUN python3 -m pip install datadog-lambda

COPY handler.py .
