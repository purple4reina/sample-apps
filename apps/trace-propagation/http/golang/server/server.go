package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/DataDog/sample-apps/apps/http/golang/internal"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func server(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	traceID := internal.TraceID(ctx)
	var msg internal.Message
	fmt.Printf("received http event body %s", event.Body)
	data, _ := base64.StdEncoding.DecodeString(event.Body)
	fmt.Printf("received http data %s", string(data))
	json.Unmarshal(data, &msg)
	ddlambda.Metric(
		"trace_context.propagated.http", 1,
		fmt.Sprintf("client_runtime:%s", msg.Runtime),
		fmt.Sprintf("server_runtime:%s", internal.Runtime),
		fmt.Sprintf("success:%t", traceID == msg.TraceID),
		"transport:http",
	)

	return events.APIGatewayProxyResponse{
		Body:       "ok",
		StatusCode: 200,
	}, nil
}

func main() {
	lambda.Start(ddlambda.WrapFunction(server, nil))
}
