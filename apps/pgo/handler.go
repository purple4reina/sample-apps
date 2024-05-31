package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"os"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

func main() {
	lambda.Start(ddlambda.WrapFunction(myHandler, nil))
}

var (
	resp = events.APIGatewayProxyResponse{
		Body:       `{"hello":"world"}`,
		StatusCode: 200,
	}
	service    = os.Getenv("DD_SERVICE")
	metricName = "custom.metric." + service
	spanName   = "custom.span." + service
	pprofFile  = "/tmp/cpu.prof"
	qParam     = "profile"
	trueVal    = "true"
)

func doIt(i int, parent ddtrace.SpanContext) {
	defer tracer.StartSpan(spanName, tracer.ChildOf(parent)).Finish()
	fmt.Printf("log %d\n", i)
	ddlambda.Metric(metricName, 1)
}

func gatherProfile() events.APIGatewayProxyResponse {
	prof, err := ioutil.ReadFile(pprofFile)
	if err != nil {
		return events.APIGatewayProxyResponse{
			Body:       fmt.Sprintf(`{"error":"%s"}`, err.Error()),
			StatusCode: 500,
		}
	}
	return events.APIGatewayProxyResponse{
		Body:       string(prof),
		StatusCode: 200,
	}
}

func myHandler(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	if val, ok := event.QueryStringParameters[qParam]; ok && val == trueVal {
		return gatherProfile(), nil
	}
	root, _ := tracer.SpanFromContext(ctx)
	for i := 0; i < 1000; i++ {
		doIt(i, root.Context())
	}
	return resp, nil
}
