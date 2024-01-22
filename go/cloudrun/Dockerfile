FROM golang

WORKDIR /app

ENV DD_ENV=dev
ENV DD_SERVICE=rey-go-cloudrun
ENV DD_TRACE_ENABLED=true
ENV DD_VERSION=1

COPY --from=datadog/serverless-init /datadog-init /app/datadog-init

COPY . ./
RUN go build -o app .

ENTRYPOINT ["/app/datadog-init"]
CMD /app/app
