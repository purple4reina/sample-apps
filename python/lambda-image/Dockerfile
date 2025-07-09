FROM public.ecr.aws/lambda/python:latest

COPY --from=public.ecr.aws/datadog/lambda-extension:latest /opt/. /opt/
ENV DD_LAMBDA_HANDLER handler.handle
CMD ["datadog_lambda.handler.handler"]

RUN python3 -m pip install datadog-lambda

# To use local dev version of datadog-lambda-python, uncomment these lines
# `cp ~/dd/datadog-lambda-python/ .datadog-lambda` before deploying
#COPY .datadog-lambda repo
#RUN pip uninstall -y datadog-lambda && \
#    python3 -m pip install repo/ && \
#    rm -rf repo/

COPY handler.py .
