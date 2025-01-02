FROM public.ecr.aws/lambda/nodejs:20

COPY --from=public.ecr.aws/datadog/lambda-extension:latest /opt/. /opt/
ENV DD_LAMBDA_HANDLER handler.handle
CMD ["node_modules/datadog-lambda-js/dist/handler.handler"]

RUN npm install datadog-lambda-js dd-trace

COPY handler.js .
