def handler(event, context):
    print(f'executing lambda handler with event {event} and context {context}')
    ret = {'Hello': 'World!'}
    try:
        return ret
    finally:
        print(f'returned {ret}')
