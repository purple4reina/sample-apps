import os
import time

start = time.time_ns()
os.environ['DD_ENV'] = 'rey'
os.environ['DD_SERVICE'] = 'rey-local-app'
os.environ['DD_INSTRUMENTATION_TELEMETRY_ENABLED'] = 'false'
os.environ['DD_API_SECURITY_ENABLED'] = 'false'

from datadog_lambda.cold_start import ColdStartTracer
from ddtrace import patch_all, tracer
patch_all()

# import more stuff here

with tracer.trace('rey-local-app') as span:
    ColdStartTracer(tracer, 'rey-local-app', start, tracer.current_trace_context(), 0, None).trace()
