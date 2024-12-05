import boto3
import os

event_bridge_client = boto3.client('events')
event_bus_name = os.environ.get('TRANSPORT_EVENT_BUS_NAME')

def handler(event, context):
    print(f'propagating to eventbridge transport {event_bus_name}')
    event_bridge_client.put_events(
        Entries=[{
            'EventBusName': event_bus_name,
            'Source': 'trace-propagation.client',
            'DetailType': 'trace-propagation-test',
            'Detail': '{"foo": "bar"}'
        }]
    )
    return 'ok'
