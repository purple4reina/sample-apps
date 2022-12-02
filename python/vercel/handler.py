import os
import secrets

if os.environ.get('REY_MANUALLY_INSTRUMENT') == 'true':
    import ddtrace
    ddtrace.patch_all()

import json
import urllib.request

url = 'http://127.0.0.1:4318/v1/traces'
with open('trace.json') as f:
    trace = json.load(f)
span = trace['resourceSpans'][0]['scopeSpans'][0]['spans'][0]

def handler(event={}, context={}):
    api_key, site = event.get('rawPath').strip('/').split('/')
    print(f'handler submitting trace to "{url}" with api key "{api_key}" '
          f'and site "{site}"')

    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    print(f'using trace_id "{trace_id}" and span_id "{span_id}"')
    span['traceId'] = trace_id
    span['spanId'] = span_id

    trace_json = json.dumps(trace)
    print(f'posting request body:\n{trace_json}')
    req = urllib.request.Request(
            url,
            method='POST',
            data=trace_json.encode(),
            headers={
                'Content-Type': 'application/json',
                'DD-SITE': site,
                'DD-API-KEY': api_key,
            },
    )

    try:
        with urllib.request.urlopen(req) as f:
            return {
                    'statusCode': f.status,
                    'body': f.read().decode() or 'ok',
            }

    except Exception as e:
        return {
                'statusCode': 500,
                'errorType': e.__class__.__name__,
                'errorMessage': str(e),
                'body': str(e),
        }

if __name__ == '__main__':
    import sys
    event = {'rawPath': sys.argv[1] + '/' + sys.argv[2]}
    print(handler(event))
