FROM node

WORKDIR /app
COPY index.js package.json ./
RUN npm install

ENV DD_SERVICE=rey-node-cloudrun
ENV DD_ENV=dev
ENV DD_VERSION=1
ENV DD_LOG_LEVEL=debug
ENV DD_TRACE_ENABLED=true
ENV DD_SITE=datadoghq.com

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init
COPY --from=datadog/dd-lib-js-init /operator-build/node_modules /dd_tracer/node/

ENTRYPOINT ["/app/datadog-init"]
CMD npm run start
