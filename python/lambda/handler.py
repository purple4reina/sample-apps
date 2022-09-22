import functools

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
