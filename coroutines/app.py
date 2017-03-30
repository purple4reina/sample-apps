import asyncio
import newrelic.agent
import time

from decorators import print_nice_transaction_trace


@newrelic.agent.coroutine_trace()
#@newrelic.agent.function_trace()
async def sleep(n):
    print(' sleep')
    await asyncio.sleep(n)
    print(' slept')


@newrelic.agent.coroutine_trace()
#@newrelic.agent.function_trace()
async def coro():
    print('enter')
    for i in range(1):
        await sleep(1)
    print('exit')


@newrelic.agent.coroutine_trace()
async def child():
    await asyncio.sleep(0)


@newrelic.agent.coroutine_trace()
async def parent():
    await child()


#@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(asyncio.gather(
        parent(),
        parent(),
    ))
    ioloop.close()


if __name__ == '__main__':
    newrelic.agent.initialize('newrelic.ini')
    app = newrelic.agent.register_application(timeout=10.0)

    print('==================================================')
    main()
    print('==================================================')
