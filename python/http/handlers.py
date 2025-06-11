import os
import requests

server_url = os.environ.get('SERVER_URL')

def client(event, context):
    print(f'making request to {server_url}')
    requests.get(server_url)
    return 'ok'

def server(event, context):
    print(f'received request: {event}')
    return 'ok'
