FROM golang:latest as build

WORKDIR /data

COPY go.mod go.sum /data
COPY handler.go /data
COPY .layer /data
RUN go mod tidy
RUN go build -tags lambda.norpc -o bootstrap handler.go

# ----------------------------

FROM public.ecr.aws/lambda/provided:al2023

COPY --from=public.ecr.aws/datadog/lambda-extension:latest /opt/. /opt/

ENV DD_API_KEY "REPLACE ME"
ENV DD_ENV "local"
ENV DD_LAMBDA_HANDLER "bootstrap"
ENV DD_LOCAL_TEST "true"
ENV DD_SERVICE "rey-golang-local"
ENV DD_SITE "datadoghq.com"
ENV DD_TRACE_ENABLED "true"
ENV DD_VERSION "0.1.0"

COPY --from=build /data/bootstrap ./bootstrap

ENTRYPOINT [ "./bootstrap" ]
