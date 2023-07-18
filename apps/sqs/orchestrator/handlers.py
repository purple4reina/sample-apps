import os
import urllib.request

producer_urls = os.environ['PRODUCER_URLS'].split(',')

def orchestrate(event, context):
    for url in producer_urls:
        print(f'calling url {url}')
        with urllib.request.urlopen(url, timeout=15) as f:
            print(f'url returned {f.read()}')
    return {'statusCode': 200, 'body': 'ok'}
