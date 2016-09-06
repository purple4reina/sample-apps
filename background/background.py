import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10)

import time
import sys

WAIT_TIME = 0

@newrelic.agent.background_task()
def main():
    time.sleep(WAIT_TIME)
    a()
    b()
    c()

@newrelic.agent.function_trace()
def a():
    time.sleep(WAIT_TIME)
    return

@newrelic.agent.function_trace()
def b():
    return a()

@newrelic.agent.function_trace()
def c():
    time.sleep(WAIT_TIME)
    return b()

if __name__ == '__main__':
    main()
    sys.exit(0)
