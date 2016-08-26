import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10)

import time

@newrelic.agent.background_task()
def main():
    time.sleep(1)
    a()
    b()
    c()

@newrelic.agent.function_trace()
def a():
    time.sleep(1)
    return

@newrelic.agent.function_trace()
def b():
    return a()

@newrelic.agent.function_trace()
def c():
    time.sleep(1)
    return b()

if __name__ == '__main__':
    main()
