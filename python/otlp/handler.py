from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

resource = Resource(attributes={
    SERVICE_NAME: 'rey-python-otlp',
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

def handler(event=None, context=None):
    with tracer.start_as_current_span('handler') as span:
        return {
                'statusCode': 200,
                'body': '{"Hello": "World"}',
        }

if __name__ == '__main__':
    handler()
