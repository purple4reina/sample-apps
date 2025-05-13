import confluent_kafka
import json
import os

def handler(event, context):
    patched = getattr(confluent_kafka, "_datadog_patch", False)
    return {
            'statusCode': 200,
            'body': json.dumps({
                'confluent_kafka._datadog_patch': patched,
                'confluent_kafka.__version__': confluent_kafka.__version__,
                'DD_DATA_STREAMS_ENABLED': os.environ.get('DD_DATA_STREAMS_ENABLED'),
            }),
    }
