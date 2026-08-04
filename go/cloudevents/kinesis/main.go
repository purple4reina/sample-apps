package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"time"

	ddlambda "github.com/DataDog/dd-trace-go/contrib/aws/datadog-lambda-go/v2"
	cloudevents "github.com/cloudevents/sdk-go/v2"
	"github.com/aws/aws-lambda-go/events"
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
// extra key is what breaks the CloudEvents SDK's strict JSON decode below.
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

func handle(ctx context.Context, event events.KinesisEvent) error {
	if len(event.Records) == 0 {
		return produce(ctx)
	}
	return consume(event)
}

// produce builds a hello-world CloudEvent and PUTs it to Kinesis.
func produce(ctx context.Context) error {
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

// consume decodes each Kinesis record as a CloudEvent. Records whose body was
// mutated by the Datadog trace-context injection fail to decode here.
func consume(event events.KinesisEvent) error {
	for _, record := range event.Records {
		ce := cloudevents.NewEvent()
		if err := json.Unmarshal(record.Kinesis.Data, &ce); err != nil {
			log.Printf("failed to decode CloudEvent from record %s: %v", record.EventID, err)
			continue
		}
		log.Printf("decoded CloudEvent: id=%s type=%s source=%s data=%s",
			ce.ID(), ce.Type(), ce.Source(), string(ce.Data()))
	}
	return nil
}
