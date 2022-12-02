import os

if os.environ.get('REY_MANUALLY_INSTRUMENT') == 'true':
    import ddtrace
    ddtrace.patch_all()

import json
import random
import secrets
import urllib.request

url = 'http://127.0.0.1:4318/v1/traces'

_words = {}
def randomized_word(api_key):
    if api_key not in _words:
        with open('/usr/share/dict/words') as f:
            ws = f.read().split('\n')
        _words[api_key] = random.choice(ws)
    return _words[api_key]

def trace_dict(api_key):
    name = randomized_word(api_key)
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {
                                "stringValue": "service-" + name
                            }
                        }
                    ]
                },
                "scopeSpans": [
                    {
                        "instrumentationLibrary": {
                            "name": "manual-test"
                        },
                        "spans": [
                            {
                                "traceId": secrets.token_hex(16),
                                "spanId": secrets.token_hex(8),
                                "name": "span-" + name,
                                "kind": 2,
                                "droppedAttributesCount": 0,
                                "events": [],
                                "attributes": [
                                    {
                                        "key": "attr1",
                                        "string_value": "attr1-" + name,
                                    },
                                    {
                                        "key": "attr2",
                                        "string_value": "attr2-" + name,
                                    }
                                ],
                                "droppedEventsCount": 0,
                                "status": {
                                    "code": 1
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }

def handler(event={}, context={}):
    api_key, site = event.get('rawPath').strip('/').split('/')
    print(f'handler submitting trace to "{url}" with api key "{api_key}" '
          f'and site "{site}"')

    trace_json = json.dumps(trace_dict(api_key))
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
                    'body': trace_json,
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
    url = 'https://example.com'
    event = {'rawPath': sys.argv[1] + '/' + sys.argv[2]}
    print(handler(event))
