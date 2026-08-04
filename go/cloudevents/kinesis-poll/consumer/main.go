package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"os"
	"time"

	cloudevents "github.com/cloudevents/sdk-go/v2"
	"github.com/aws/aws-sdk-go-v2/aws"
	awscfg "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/kinesis"
	"github.com/aws/aws-sdk-go-v2/service/kinesis/types"
)

// A plain, uninstrumented Kinesis reader: no dd-trace-go, no Lambda. It
// manually pulls records from the stream and decodes each one as a
// CloudEvent, so you can watch decode failures caused by the producer's
// trace-context injection without any consumer-side instrumentation muddying
// the picture.
func main() {
	streamName := os.Getenv("KINESIS_STREAM_NAME")
	if streamName == "" {
		log.Fatal("KINESIS_STREAM_NAME must be set")
	}

	ctx := context.Background()
	awsCfg, err := awscfg.LoadDefaultConfig(ctx)
	if err != nil {
		log.Fatalf("failed to load AWS config: %v", err)
	}
	client := kinesis.NewFromConfig(awsCfg)

	shardIterator, err := initialShardIterator(ctx, client, streamName)
	if err != nil {
		log.Fatalf("failed to get shard iterator: %v", err)
	}

	log.Printf("polling stream %q for CloudEvents...", streamName)
	for {
		out, err := client.GetRecords(ctx, &kinesis.GetRecordsInput{ShardIterator: shardIterator})
		if err != nil {
			log.Fatalf("GetRecords failed: %v", err)
		}

		for _, record := range out.Records {
			decodeRecord(record)
		}

		if out.NextShardIterator == nil {
			log.Println("shard closed, exiting")
			return
		}
		shardIterator = out.NextShardIterator

		if len(out.Records) == 0 {
			time.Sleep(2 * time.Second)
		}
	}
}

func initialShardIterator(ctx context.Context, client *kinesis.Client, streamName string) (*string, error) {
	shards, err := client.ListShards(ctx, &kinesis.ListShardsInput{StreamName: aws.String(streamName)})
	if err != nil {
		return nil, err
	}
	if len(shards.Shards) == 0 {
		return nil, errors.New("stream has no shards")
	}

	out, err := client.GetShardIterator(ctx, &kinesis.GetShardIteratorInput{
		StreamName:        aws.String(streamName),
		ShardId:           shards.Shards[0].ShardId,
		ShardIteratorType: types.ShardIteratorTypeTrimHorizon,
	})
	if err != nil {
		return nil, err
	}
	return out.ShardIterator, nil
}

func decodeRecord(record types.Record) {
	ce := cloudevents.NewEvent()
	if err := json.Unmarshal(record.Data, &ce); err != nil {
		log.Printf("failed to decode CloudEvent from record %s: %v", aws.ToString(record.SequenceNumber), err)
		return
	}
	log.Printf("decoded CloudEvent: id=%s type=%s source=%s data=%s",
		ce.ID(), ce.Type(), ce.Source(), string(ce.Data()))
}
