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

with tracer.span(name="main") as span:
    with tracer.span(name="main") as span:
       time.sleep(0.5)
