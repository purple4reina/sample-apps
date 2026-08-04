package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	cloudevents "github.com/cloudevents/sdk-go/v2"
)

func main() {
	body, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "failed to read stdin:", err)
		os.Exit(1)
	}

	event := cloudevents.NewEvent()
	if err := json.Unmarshal(body, &event); err != nil {
		fmt.Fprintln(os.Stderr, "failed to decode CloudEvent:", err)
		os.Exit(1)
	}

	fmt.Printf("decoded CloudEvent: id=%s type=%s source=%s data=%s\n",
		event.ID(), event.Type(), event.Source(), string(event.Data()))
}
