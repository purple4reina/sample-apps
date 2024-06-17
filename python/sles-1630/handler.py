from my_logging import logger

def handler(event, context):
    logger.info('This is a log message')
    print('this line is printed')
    return 'ok'
