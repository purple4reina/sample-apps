import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

from context import Context
import events


@newrelic.agent.lambda_handler()
def handler(event, context):
    return {}


if __name__ == '__main__':
    handler({}, Context())
