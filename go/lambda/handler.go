package main

import (
	"context"
	"fmt"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func main() {
	lambda.Start(ddlambda.WrapFunction(logInputOutput(myHandler), nil))
}

type handlerFunc func(context.Context, events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error)

func logInputOutput(handler handlerFunc) handlerFunc {
	return func(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
		fmt.Printf("🎭🎭🎭🎭🎭 function received context: %#v\n", ctx)
		fmt.Printf("🎭🎭🎭🎭🎭 function received event: %#v\n", event)
		str, err := handler(ctx, event)
		fmt.Printf("🎭🎭🎭🎭🎭 function returned result: %#v\n", str)
		fmt.Printf("🎭🎭🎭🎭🎭 function returned error: %#v\n", err)
		return str, err
	}
}

var (
	body = "🎨🎨🎨🎨🎨 Hello World! 🎨🎨🎨🎨🎨"
	resp = events.APIGatewayProxyResponse{
		Body:       body,
		StatusCode: 200,
	}
)

func myHandler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	fmt.Println(body)
	return resp, nil
}
