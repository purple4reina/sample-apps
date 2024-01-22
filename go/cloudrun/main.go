package main

import (
	"fmt"
	"net/http"
	"time"

	httptrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/net/http"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

func main() {
	tracer.Start()
	defer tracer.Stop()

	go background()

	http.HandleFunc("/", handler)
	_ = http.ListenAndServe(":8080", nil)
}

var client = httptrace.WrapClient(http.DefaultClient)

func handler(w http.ResponseWriter, r *http.Request) {
	_, _ = client.Get("https://example.com")
	fmt.Fprintf(w, "ok")
}

func background() {
	t := time.NewTicker(time.Second)
	for _ = range t.C {
		_, _ = client.Get("https://example.com")
	}
}
