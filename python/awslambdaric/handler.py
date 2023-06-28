import json
import os.path
import urllib.request

class cold: start = True

def is_extension_exists():
    return os.path.exists('/opt/extensions/datadog-agent')

def is_extension_running():
    try:
        urllib.request.urlopen('http://127.0.0.1:8124/lambda/hello')
        return True
    except Exception as e:
        print(f'error pinging extzension: [{e.__class__.__name__}] {e}')
        return False

def handler(event, context):
    try:
        return {
                'statusCode': 200,
                'body': json.dumps({
                    'cold_start': cold.start,
                    'extension_exists': is_extension_exists(),
                    'extension_running': is_extension_running(),
                }),
        }
    finally:
        cold.start = False

if __name__ == '__main__':
    print(handler({},{}))
