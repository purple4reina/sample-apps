import time

from ddtrace import tracer

def handle(event, context):
    with tracer.trace('start'):
        time.sleep(0.01)
    with tracer.trace('importing'):
        import requests
    with tracer.trace('end'):
        time.sleep(0.01)
    return 'ok'
