import os

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import redis
import time

REDIS_HOST = '172.17.0.8'
NUMBER_OF_GETS = 10**5

def _log(*msg):
    print '--> ' + ' '.join(map(str, msg))

def main():
    r = redis.StrictRedis(host=REDIS_HOST)
    r.flushall()

    for num in xrange(NUMBER_OF_GETS):
        r.delete(num)
        r.set(num, num)
        r.get(num)

def percent_change(final, initial):
    return (final - initial) * 100 / initial

if __name__ == '__main__':

    _log('Run benchmarking with agent')
    start_with = time.time()
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'redis'):
        main()
    end_with = time.time()

    _log('Run benchmarking without agent')
    start_without = time.time()
    main()
    end_without = time.time()

    time_with = end_with - start_with
    time_without = end_without - start_without

    _log('Time with is        :', time_with, 'seconds')
    _log('Time without is     :', time_without, 'seconds')

    percent_increase = percent_change(time_with, time_without)
    _log('Percent increase is :', percent_increase, '%')
