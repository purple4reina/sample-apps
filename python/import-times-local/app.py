import os
import time

start = time.time_ns()
os.environ['AWS_LAMBDA_FUNCTION_NAME'] = 'rey-local-app'
os.environ['DD_API_SECURITY_ENABLED'] = 'false'
os.environ['DD_ENV'] = 'rey'
os.environ['DD_INSTRUMENTATION_TELEMETRY_ENABLED'] = 'false'
os.environ['DD_SERVICE'] = 'rey-local-app'

from datadog_lambda.cold_start import ColdStartTracer
from ddtrace import patch_all, tracer
patch_all()

# import more stuff here

with tracer.trace('rey-local-app') as span:
    ColdStartTracer(tracer, 'rey-local-app', start, tracer.current_trace_context(), 0, None).trace()
