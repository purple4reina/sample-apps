import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import redis

REDIS_HOST = 'localhost'


@newrelic.agent.background_task()
def main():
    r = redis.StrictRedis(host=REDIS_HOST)
    r.ping()
    r.set('key', 'value')
    r.get('key')


if __name__ == '__main__':
    main()
