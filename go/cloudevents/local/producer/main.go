package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	cloudevents "github.com/cloudevents/sdk-go/v2"
)

func main() {
	event := cloudevents.NewEvent()
	event.SetID("hello-world-1")
	event.SetSource("sample-apps/cloudevents")
	event.SetType("com.datadoghq.sample.hello")
	event.SetTime(time.Now())
	if err := event.SetData(cloudevents.ApplicationJSON, map[string]string{"message": "hello world"}); err != nil {
		fmt.Fprintln(os.Stderr, "failed to set event data:", err)
		os.Exit(1)
	}

	body, err := json.Marshal(event)
	if err != nil {
		fmt.Fprintln(os.Stderr, "failed to marshal event:", err)
		os.Exit(1)
	}

	os.Stdout.Write(body)
}
