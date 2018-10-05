import newrelic.agent
newrelic.agent.initialize('newrelic.ini')


@newrelic.agent.lambda_handler()
def handler(event, context):
    pass


if __name__ == '__main__':
    handler({}, {})
