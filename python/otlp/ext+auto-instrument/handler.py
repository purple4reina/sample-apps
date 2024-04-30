import time

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def handler(event, context):
    with tracer.start_as_current_span('my-function'):
        time.sleep(0.1)
        return 'ok'
