import time
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import always_on
from ocnewrelic import NewRelicExporter

newrelic = NewRelicExporter(
        license_key='3df7cbd6552a53d944c433993f208b5226634086',
        service_name='OpenCensus-Python',
)

tracer = Tracer(
        exporter=newrelic,
        sampler=always_on.AlwaysOnSampler(),
)

with tracer.span(name='main') as span:
    tracer.add_attribute_to_current_span('mykey', 'myvalue-parent')
    with tracer.span(name='child') as span:
        tracer.add_attribute_to_current_span('mykey', 'myvalue-child')
        time.sleep(0.5)
