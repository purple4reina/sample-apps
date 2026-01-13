import json

from aws_durable_execution_sdk_python import durable_execution, DurableContext

@durable_execution
def handler(event, context):
    return event
