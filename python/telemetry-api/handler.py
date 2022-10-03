import time
start = time.time()

try:
    import functools
    import os

    env_sleep = os.environ.get('REY_INIT_SLEEP_TIME', 0)
    env_fail_first = os.environ.get('REY_INIT_FAIL_FIRST_TIME') == 'true'
    env_fail_second = os.environ.get('REY_INIT_FAIL_SECOND_TIME') == 'true'

    print('found environment:\n'
          f'REY_INIT_SLEEP_TIME={env_sleep}\n'
          f'REY_INIT_FAIL_FIRST_TIME={env_fail_first}\n'
          f'REY_INIT_FAIL_SECOND_TIME={env_fail_second}')

    print(f'sleeping for {env_sleep} seconds')
    time.sleep(env_sleep)

    init_count_file = '/tmp/init-count'
    init_count = 1
    if os.path.exists(init_count_file):
        with open(init_count_file) as f:
            init_count = int(f.read() or 0) + 1
    with open(init_count_file, 'w') as f:
        f.write(str(init_count))

    print(f'first init will fail: {env_fail_first}\n'
          f'second init will fail: {env_fail_second}\n'
          f'this is init number {init_count}')

    if init_count == 1:
        assert not env_fail_first, 'oops, first init failed'
    elif init_count == 2:
        assert not env_fail_second, 'oops, second init failed'

finally:
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
