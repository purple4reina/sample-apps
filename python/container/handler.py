import os
import time

start = time.time()
import ddtrace
diff = time.time() - start

cold_start = True

def handler(event, context):
    global cold_start
    try:
        if cold_start:
            from metric import statsd
            statsd.distribution('rey.ddtrace.import', diff, tags=[
                f'git_sha:{os.environ.get("GIT_SHA")}',
                'local:true',
            ])
    finally:
        cold_start = False
    return 'ok'
