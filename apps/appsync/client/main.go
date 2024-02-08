package main

import (
	"bytes"
	"context"
	"io"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-xray-sdk-go/xray"

	ddlambda "github.com/DataDog/datadog-lambda-go"
)

func main() {
	lambda.Start(ddlambda.WrapFunction(myHandler, nil))
}

func myHandler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	client := xray.Client(http.DefaultClient)
	req, err := http.NewRequest(
		"POST",
		"https://eo26flswmnbyjm22qq5uifkc4i.appsync-api.sa-east-1.amazonaws.com/graphql",
		bytes.NewBuffer([]byte(`{"query":"query MyQuery { hello(id: \"\") }"}`)),
	)
	if err != nil {
		panic(err)
	}
	req.Header.Set("x-api-key", "da2-yuyeeslhc5hjplmtb7lsqccjze")
	req = req.WithContext(ctx)
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	return events.APIGatewayProxyResponse{
		Body:       string(body),
		StatusCode: 200,
	}, nil
}
