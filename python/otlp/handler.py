import time

from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# change this from grpc to http for http transports
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource(attributes={
    SERVICE_NAME: 'rey-python-otlp',
})
endpoint = 'http://localhost:4317'

# initialize tracer
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint+'/v1/traces'))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# initialize metrics
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint+'/v1/metrics'))
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)

kitten_counter = meter.create_counter(
        name='kittens', unit='kittens', description='number of kittens found')

@tracer.start_as_current_span('function')
def function():
    kitten_counter.add(1, dict(name='pamina'))
    time.sleep(1)

@tracer.start_as_current_span('handler')
def handler(event=None, context=None):
    function()
    return {
            'statusCode': 200,
            'body': '{"Hello": "World"}',
    }

if __name__ == '__main__':
    handler()
