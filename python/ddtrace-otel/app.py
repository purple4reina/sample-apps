from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("ddtrace-otel-span") as span:
    span.set_attribute("key", "value")
