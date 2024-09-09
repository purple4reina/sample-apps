from aws_cdk import App

from datadog_cdk_constructs_v2 import Datadog, DatadogProps

app = App()

Datadog(
    app,
    "Datadog",
)
