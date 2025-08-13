package main

import (
	"context"
	"os"

	ddlambda "github.com/DataDog/datadog-lambda-go"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	awscfg "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
	awstrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/aws/aws-sdk-go-v2/aws"
)

var (
	sqsClient = func() *sqs.Client {
		awsCfg, _ := awscfg.LoadDefaultConfig(context.TODO())
		awstrace.AppendMiddleware(&awsCfg)
		return sqs.NewFromConfig(awsCfg)
	}()
	sqsMsgInput = &sqs.SendMessageInput{
		QueueUrl:    aws.String(os.Getenv("SQS_QUEUE_URL")),
		MessageBody: aws.String("hello"),
	}
)

func main() {
	lambda.Start(ddlambda.WrapFunction(handle, nil))
}

func handle(ctx context.Context, event events.SQSEvent) error {
	var err error
	if len(event.Records) == 0 {
		_, err = sqsClient.SendMessage(ctx, sqsMsgInput)
	}
	return err
}
