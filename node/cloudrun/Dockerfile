FROM node

WORKDIR /app
COPY package.json .
RUN npm i
COPY . .

ENV DD_SERVICE=rey-node-cloudrun
ENV DD_ENV=dev
ENV DD_VERSION=1
ENV DD_LOG_LEVEL=DEBUG

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init

ENTRYPOINT ["/app/datadog-init"]
CMD npm run start
