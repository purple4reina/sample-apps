import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

resource = Resource(attributes={
    SERVICE_NAME: 'rey-python-otlp',
})

provider = TracerProvider(resource=resource)
#processor = BatchSpanProcessor(ConsoleSpanExporter())
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint='http://localhost:4318/v1/traces'))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span('function')
def function():
    time.sleep(5)

@tracer.start_as_current_span('handler')
def handler(event=None, context=None):
    function()
    return {
            'statusCode': 200,
            'body': '{"Hello": "World"}',
    }

if __name__ == '__main__':
    handler()
