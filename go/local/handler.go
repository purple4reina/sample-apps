package main

import (
	"context"
	"fmt"
	"time"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func main() {
	lambda.Start(ddlambda.WrapFunction(myHandler, &ddlambda.Config{
		//BlockMetricsAtCapacity: true,
	}))
}

var metricName = "rey.golang.fast_metric"

func myHandler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	ctx, _ = context.WithTimeout(ctx, 1*time.Second)
	var i int
	for {
		i++
		if i%1000 == 0 {
			fmt.Printf("i: %#v\n", i)
		}
		ddlambda.Metric(metricName, 1)
		select {
		case <-ctx.Done():
			return events.APIGatewayProxyResponse{
				Body:       fmt.Sprintf(`{"metrics": %d}`, i),
				StatusCode: 200,
			}, nil
		default:
		}
	}
}
