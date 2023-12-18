import newrelic.agent
newrelic.agent.initialize()
newrelic.agent.register_application(timeout=10.0)

import redis
import gc


@newrelic.agent.background_task()
def main():
    r = redis.Redis()
    for _ in range(10000):
        with r.pipeline(transaction=False) as pipe:
            pipe.set('foo', 'bar')
            pipe.set('bar', 'baz')
            pipe.get('foo')
            pipe.get('bar')
            results = pipe.execute()
            print('results: ', results)


if __name__ == '__main__':
    main()
