package main

import (
	"context"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	"go.opentelemetry.io/contrib/instrumentation/github.com/aws/aws-lambda-go/otellambda"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
	"go.opentelemetry.io/otel/trace"
)

var (
	endpoint    = os.Getenv("DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_HTTP_ENDPOINT")
	resp        = `{"cold_start":true,"runtime":"golang"}`
	serviceName = "rey-app-otlp-dev-golang"

	tracer trace.Tracer
)

func HandleRequest(ctx context.Context, request interface{}) (string, error) {
	defer func() { resp = `{"cold_start":false,"runtime":"golang"}` }()

	ctx, span := tracer.Start(ctx, "handler")
	defer span.End()
	ctx, span = tracer.Start(ctx, "function")
	defer span.End()

	time.Sleep(time.Second)

	return resp, nil
}

func main() {
	ctx := context.Background()
	resource := resource.NewSchemaless(
		semconv.ServiceName(serviceName),
	)
	exp, _ := otlptracehttp.New(ctx,
		otlptracehttp.WithEndpoint(endpoint),
		otlptracehttp.WithInsecure(),
	)
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(resource),
	)
	tracer = tp.Tracer(serviceName)

	lambda.Start(
		otellambda.InstrumentHandler(HandleRequest,
			otellambda.WithTracerProvider(tp),
			otellambda.WithFlusher(tp),
		))
}
