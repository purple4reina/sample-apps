import time

import newrelic.agent
from decorators import print_nice_transaction_trace


@newrelic.agent.coroutine_trace()
def coro():
    print('enter coro')
    for i in range(3):
        time.sleep(0.1)
        try:
            resp = yield i
        except ZeroDivisionError:
            raise
    print('exit coro')


#@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    c = coro()
    c.send(None)
    print('done')


if __name__ == '__main__':
    newrelic.agent.initialize('newrelic.ini')
    app = newrelic.agent.register_application(timeout=10.0)

    print('==================================================')
    main()
    print('==================================================')
