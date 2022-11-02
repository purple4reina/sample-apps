package main

import (
	"context"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func main() {
	lambda.Start(ddlambda.WrapFunction(myHandler, nil))
}

var resp = events.APIGatewayProxyResponse{
	Body:       `{"hello":"world"}`,
	StatusCode: 200,
}

func myHandler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	return resp, nil
}
