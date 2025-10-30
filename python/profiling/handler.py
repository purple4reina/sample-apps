import time

def handler(event, context):
    end = time.time() + 65
    while time.time() < end:
        pass
    return 'ok'
