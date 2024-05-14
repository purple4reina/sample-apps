FROM public.ecr.aws/lambda/nodejs:20

COPY --from=public.ecr.aws/datadog/lambda-extension:51 /opt/extensions/ /opt/extensions
ENV DD_LAMBDA_HANDLER handler.handle
CMD ["node_modules/datadog-lambda-js/dist/handler.handler"]

RUN npm install datadog-lambda-js dd-trace

COPY handler.js .
