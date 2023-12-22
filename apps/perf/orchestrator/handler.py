import json
import os
import urllib.request

function_urls = os.environ['FUNCTION_URLS'].split(',')

def handler(event, context):
    resp = {}
    for url in function_urls:
        try:
            print(f'calling url {url}')
            with urllib.request.urlopen(url, timeout=15) as f:
                resp[url] = f.read().decode()
        except Exception as e:
            resp[url] = f'error calling url: [{e.__class__.__name__}] {e}'
    return {'statusCode': 200, 'body': json.dumps(resp)}
