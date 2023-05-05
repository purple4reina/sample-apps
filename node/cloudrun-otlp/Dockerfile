# gcloud run deploy rey-otlp-gcp-node --update-env-vars=DD_API_KEY=$DD_API_KEY --allow-unauthenticated --source .

FROM node

WORKDIR /app
COPY package.json index.js instrument.js /app/
RUN npm i

ENV NODE_OPTIONS="--require ./instrument"
ENV DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_HTTP_ENDPOINT="localhost:4318"

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init
ENTRYPOINT ["/app/datadog-init"]

CMD npm run start
