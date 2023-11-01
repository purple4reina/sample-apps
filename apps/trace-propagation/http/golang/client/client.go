package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/DataDog/sample-apps/apps/http/golang/internal"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

var (
	httpClient = http.DefaultClient
	serverUrls = strings.Split(os.Getenv("SERVER_URLS"), ",")
)

func client(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	data, _ := json.Marshal(internal.Message{
		Runtime: internal.Runtime,
		TraceID: internal.TraceID(ctx),
	})
	span, _ := tracer.SpanFromContext(ctx)

	for _, url := range serverUrls {
		fmt.Printf("calling %s with data %s\n", url, string(data))
		req, _ := http.NewRequest("GET", url, strings.NewReader(string(data)))
		tracer.Inject(span.Context(), tracer.HTTPHeadersCarrier(req.Header))
		httpClient.Do(req)
	}

	return events.APIGatewayProxyResponse{
		Body:       "ok",
		StatusCode: 200,
	}, nil
}

func main() {
	lambda.Start(ddlambda.WrapFunction(client, nil))
}
