def handler(event, context):
    print(f'🐚🐚🐚🐚🐚 got event: {event} 🐚🐚🐚🐚🐚')
    print(f'🐚🐚🐚🐚🐚 got context: {context} 🐚🐚🐚🐚🐚')
    return {'Hello': 'World!'}
