import urllib.request

url = 'http://127.0.0.1:4318/v1/traces'
with open('trace.json') as f:
    data = f.read()
trace_json = data.encode()

def handler(event={}, context={}):
    api_key = event.get('rawPath').strip('/')
    print(f'handler submitting trace to "{url}" with api key "{api_key}"')

    req = urllib.request.Request(url, method='POST', data=trace_json, headers={
        'Content-Type': 'application/json',
        'DD-SITE': 'datadoghq.com',
        'DD-API-KEY': api_key,
    })

    try:
        with urllib.request.urlopen(req) as f:
            return {
                    'statusCode': f.status,
                    'body': f.read().decode(),
            }

    except Exception as e:
        return {
                'statusCode': 500,
                'errorType': e.__class__.__name__,
                'errorMessage': str(e),
                'body': str(e),
        }

if __name__ == '__main__':
    url = 'http://example.com'
    print(handler())
