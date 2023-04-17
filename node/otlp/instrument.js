const { NodeTracerProvider } = require("@opentelemetry/sdk-trace-node");
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');

const serviceName = process.env.DD_SERVICE || 'rey-node-otlp';
const endpoint = `http://${(
    process.env.DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_HTTP_ENDPOINT ||
    process.env.DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_GRPC_ENDPOINT ||
    'localhost:4318'
)}`

const provider = new NodeTracerProvider({
  resource: new Resource({
    [ SemanticResourceAttributes.SERVICE_NAME ]: serviceName,
  })
});

provider.addSpanProcessor(
  new SimpleSpanProcessor(
    new OTLPTraceExporter(
      { url: endpoint+'/v1/traces' },
    ),
  ),
);
provider.register();

registerInstrumentations({
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-aws-lambda': {
        disableAwsContextPropagation: true,
      },
    }),
  ],
});

