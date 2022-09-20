def handler(event, context):
    print(f'executing lambda handler with event {event} and context {context}')
    return {'Hello': 'World!'}
