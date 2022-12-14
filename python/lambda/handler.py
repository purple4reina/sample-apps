def handler(event, context):
    print('handler received event:', event)
    print('handler received context:', context)
    return {
            'statusCode': 200,
            'body': '{"Hello": "World"}',
    }
