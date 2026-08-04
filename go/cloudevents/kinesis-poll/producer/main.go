package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"time"

	ddlambda "github.com/DataDog/dd-trace-go/contrib/aws/datadog-lambda-go/v2"
	cloudevents "github.com/cloudevents/sdk-go/v2"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	awscfg "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kinesis"
	awstrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/aws/aws-sdk-go-v2/aws"
)

// kinesisClient is instrumented with dd-trace-go's AWS SDK v2 middleware. On
// every PutRecord call this middleware splices a top-level "_datadog" key
// into the record's JSON body to propagate trace/DSM context (see
// dd-trace-go/contrib/aws/aws-sdk-go-v2/internal/kinesis/kinesis.go). That
// extra key is what breaks the CloudEvents SDK's strict JSON decode in the
// consumer.
var kinesisClient = func() *kinesis.Client {
	awsCfg, err := awscfg.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("failed to load AWS config: %v", err)
	}
	awstrace.AppendMiddleware(&awsCfg)
	return kinesis.NewFromConfig(awsCfg)
}()

func main() {
	lambda.Start(ddlambda.WrapFunction(handle, nil))
}

// handle builds a hello-world CloudEvent and PUTs it to Kinesis. Invoke this
// function directly (e.g. via its function URL) to produce one record.
func handle(ctx context.Context, _ struct{}) error {
	ce := cloudevents.NewEvent()
	ce.SetID("hello-world-1")
	ce.SetSource("sample-apps/cloudevents")
	ce.SetType("com.datadoghq.sample.hello")
	ce.SetTime(time.Now())
	if err := ce.SetData(cloudevents.ApplicationJSON, map[string]string{"message": "hello world"}); err != nil {
		return err
	}

	body, err := json.Marshal(ce)
	if err != nil {
		return err
	}

	_, err = kinesisClient.PutRecord(ctx, &kinesis.PutRecordInput{
		StreamName:   aws.String(os.Getenv("KINESIS_STREAM_NAME")),
		PartitionKey: aws.String("hello-world"),
		Data:         body,
	})
	return err
}
