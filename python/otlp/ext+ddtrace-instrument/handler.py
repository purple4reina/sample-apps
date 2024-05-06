import time

from opentelemetry import trace
from ddtrace.opentelemetry import TracerProvider

provider = TracerProvider()
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

def handler(event=None, context=None):
    with tracer.start_as_current_span('my-function'):
        time.sleep(0.1)
        return 'ok'

# add lambda instrumentation, done last bc wraps handler func
from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor
AwsLambdaInstrumentor().instrument()
