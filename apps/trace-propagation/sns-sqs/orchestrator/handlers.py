import os
import urllib.request

producer_urls = os.environ['PRODUCER_URLS'].split(',')

def orchestrate(event, context):
    resp = {'statusCode': 200, 'body': 'ok'}
    for url in producer_urls:
        try:
            print(f'calling url {url}')
            with urllib.request.urlopen(url, timeout=15) as f:
                print(f'url returned {f.read()}')
        except Exception as e:
            err = f'error calling url: [{e.__class__.__name__}] {e}'
            resp.setdefault('errors', []).append(err)
            resp['statusCode'] = 500
    return resp
