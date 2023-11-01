import os
import requests

client_urls = os.environ['CLIENT_URLS'].split(',')

def orchestrate(event, context):
    resp = {'statusCode': 200, 'body': 'ok'}
    for url in client_urls:
        try:
            print(f'calling url {url}')
            requests.get(url)
        except Exception as e:
            err = f'error calling url: [{e.__class__.__name__}] {e}'
            resp.setdefault('errors', []).append(err)
            resp['statusCode'] = 500
    return resp
