package internal

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"strings"

	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

var Runtime = strings.ReplaceAll(os.Getenv("AWS_EXECUTION_ENV"), "AWS_Lambda_", "")

type Message struct {
	Runtime string `json:"runtime"`
	TraceID string `json:"trace_id"`
}

func TraceID(ctx context.Context) string {
	span, _ := tracer.SpanFromContext(ctx)
	spanCtx := span.Context()
	spanID, traceID := spanCtx.SpanID(), spanCtx.TraceID()
	fmt.Printf("found span context spanid=%s traceid=%s\n", spanID, traceID)
	return strconv.FormatUint(traceID, 10)
}
