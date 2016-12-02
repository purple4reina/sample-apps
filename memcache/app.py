import newrelic
import newrelic.agent
newrelic.agent.initialize('/data/newrelic.ini')
APP = newrelic.agent.register_application(timeout=10.0)

import functools
import memcache
import random

MEMCACHE_ADDR_1 = 'memcache1:11211'
MEMCACHE_ADDR_2 = 'memcache2:11211'
MEMCACHE_ADDR_3 = 'memcache3:11211'

def rand():
    return str(random.randrange(1, 100))

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def _exercise_it(client):
    client.set(rand(), 'world')

server_usage = {}

def wrap_get_server(fn):
    @functools.wraps(fn)
    def wraps(*args, **kwargs):
        server, key = fn(*args, **kwargs)
        server_usage[server] = server_usage.get(server, 0) + 1
        print 'server: ', server
        return server, key
    return wraps

def main():
    servers = [
        (MEMCACHE_ADDR_1, 1),
        (MEMCACHE_ADDR_2, 1),
        (MEMCACHE_ADDR_3, 5),
    ]
    client = memcache.Client(servers, debug=True)

    client._get_server = wrap_get_server(client._get_server)

    for _ in xrange(1000):
        _exercise_it(client)

    _log(server_usage)

    _log(client.get_slabs())

if __name__ == '__main__':
    _log('Using agent version', newrelic.version)
    with newrelic.agent.BackgroundTask(APP, 'memcache'):
        main()
