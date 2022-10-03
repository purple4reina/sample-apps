import time
start = time.time()

import functools
import os

sleep_time = float(os.environ.get('REY_INIT_SLEEP_TIME', 0))
print(f'sleeping for {sleep_time} seconds')
time.sleep(sleep_time)

should_fail = os.environ.get('REY_INIT_FAIL', 'False').lower() in ('true', '1')
print(f'init will fail: {should_fail}')
assert not should_fail, 'oops, init failed'

end = time.time()
print(f'init code block took {end-start} sec to run')

def log_request_response(fn):
    @functools.wraps(fn)
    def log(event, context):
        print(f'executing lambda handler {fn.__name__} with event {event} and context {context}')
        try:
            ret = fn(event, context)
            print(f'handler returned {ret}')
            return ret
        except Exception as e:
            print(f'handler raised exception: [{e.__class__.__name__}] {e}')
            raise
    return log

@log_request_response
def handler(event, context):
    return {
            'statusCode': 200,
            'body': '{"Hello": "World"}',
    }
