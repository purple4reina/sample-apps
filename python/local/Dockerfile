FROM public.ecr.aws/lambda/python:latest

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions
ENV DD_LAMBDA_HANDLER handler.handle
CMD ["datadog_lambda.handler.handler"]

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY handler.py .
