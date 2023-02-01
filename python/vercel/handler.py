import json
import os
import random
import secrets
import time
import urllib.request

url = 'http://127.0.0.1:4318/v1/traces'

def trace_dict():
    with open('trace.json') as f:
        trace = json.load(f)

    trace_id = secrets.token_hex(16)
    span_id_translator = {}
    time_now = time.time() * 10**9
    time_ref = int(trace['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['startTimeUnixNano'])
    time_delta = time_now - time_ref

    for resource_span in trace['resourceSpans']:
        for scope_span in resource_span['scopeSpans']:
            for span in scope_span['spans']:
                old_span_id = span['spanId']
                span_id_translator[old_span_id] = secrets.token_hex(8)

    for resource_span in trace['resourceSpans']:
        for scope_span in resource_span['scopeSpans']:
            for span in scope_span['spans']:
                span['traceId'] = trace_id
                span['spanId'] = span_id_translator[span['spanId']]
                parent_id = span.get('parentSpanId')
                if parent_id:
                    span['parentSpanId'] = span_id_translator[span['parentSpanId']]
                start = int(span['startTimeUnixNano']) + time_delta
                span['startTimeUnixNano'] = f'{start:.0f}'
                end = int(span['endTimeUnixNano']) + time_delta
                span['endTimeUnixNano'] = f'{end:.0f}'

    return trace

def handler(event={}, context={}):
    try:
        api_key, site = event.get('rawPath').strip('/').split('/')
    except:
        api_key = os.environ.get('DD_API_KEY')
        site = 'datadoghq.com'
    print(f'handler submitting trace to "{url}" with api key "{api_key}" '
          f'and site "{site}"')

    trace_json = json.dumps(trace_dict())
    print(f'handler posting request body:\n{trace_json}')
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
                    'body': trace_json,
            }

    except Exception as e:
        return {
                'statusCode': 500,
                'errorType': e.__class__.__name__,
                'errorMessage': str(e),
                'body': 'handler request received error: ' + str(e),
        }

if __name__ == '__main__':
    import sys
    url = 'https://example.com'
    event = {'rawPath': sys.argv[1] + '/' + sys.argv[2]}
    print(handler(event))
