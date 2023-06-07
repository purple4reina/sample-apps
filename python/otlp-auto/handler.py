def handler(event, context):
    return {'statusCode': 200, 'body': 'ok'}

if __name__ == '__main__':
    from context import lambda_context
    print(handler({}, lambda_context))
