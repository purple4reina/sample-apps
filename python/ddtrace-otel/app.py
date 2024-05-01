from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def handler(event, context):
    with tracer.start_as_current_span("ddtrace-otel-span") as span:
        span.set_attribute("key", "value")

if __name__ == '__main__':
    handler({}, {})
