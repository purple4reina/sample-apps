import asyncio
import newrelic.agent
import time

from decorators import print_nice_transaction_trace, validate_tt_parenting


#@newrelic.agent.function_trace()
async def sleep(n):
    await asyncio.sleep(n)


#@newrelic.agent.coroutine_trace()
@newrelic.agent.function_trace()
async def coro():
    print('enter')
    for i in range(2):
        await sleep(0.00001)
    print('exit')


tt = (
    '__main__:main', [
        ('__main__:coro', []),
        ('__main__:coro', []),
    ]
)


@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(asyncio.gather(
        coro(), coro(),
    ))
    ioloop.close()


if __name__ == '__main__':
    newrelic.agent.initialize('newrelic.ini')
    app = newrelic.agent.register_application(timeout=10.0)

    print('==================================================')
    main()
    print('==================================================')
