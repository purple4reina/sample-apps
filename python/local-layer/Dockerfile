FROM public.ecr.aws/lambda/python:3.9

RUN yum install gcc -y

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions
CMD ["datadog_lambda.handler.handler"]

COPY .tracer/ tracer/
RUN SETUPTOOLS_SCM_PRETEND_VERSION=2.8.0 pip install -U tracer/ -t /opt/python/ && rm -rf tracer/

COPY handler.py .
COPY vendor/ /opt/python/

ENV DD_ENV "local"
ENV DD_LAMBDA_HANDLER "handler.handle"
ENV DD_LOCAL_TEST "true"
ENV DD_SERVICE "rey-lambda-local"
ENV DD_SITE "datadoghq.com"
ENV DD_TRACE_ENABLED "true"
ENV DD_VERSION "0.1.0"

ENV DD_COLD_START_TRACE_SKIP_LIB ""
ENV DD_MIN_COLD_START_DURATION "0"

#ENV DD_PROFILING_ENABLED "true"

#RUN rm -rf /opt/python/google/_upb
