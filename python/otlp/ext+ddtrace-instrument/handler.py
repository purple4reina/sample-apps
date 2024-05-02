import time

from ddtrace.opentelemetry import TracerProvider
from opentelemetry import trace

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

def handler(event, context):
    with tracer.start_as_current_span('my-function'):
        time.sleep(0.1)
        return 'ok'

# add lambda instrumentation, done last bc wraps handler func
from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor
AwsLambdaInstrumentor().instrument()
