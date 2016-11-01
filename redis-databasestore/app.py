import os

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import random
import redis

REDIS_HOST = '172.17.0.8'  # if using docker use this one
REDIS_HOST = 'localhost'

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def redis_class():
    # This class is only for backward compatability
    r = redis.Redis(host=REDIS_HOST)

    _log('Attempting to ping')
    r.ping()
    _log('Successfully pinged!')

    _log('Adding a key')
    key = 'thing'
    value = 'deathray'
    r.set(key, value)

    _log('Getting that key')
    gotten_value = r.get(key)

    _log('Do they match?')
    assert gotten_value == value
    _log('They match!')

def strict_redis_class():
    r = redis.StrictRedis(host=REDIS_HOST)

    _log('Attempting to ping')
    r.ping()
    _log('Successfully pinged!')

    _log('I want to know how many keys there are')
    keys = r.keys()
    _log('These are they keys', keys)

    _log('Now delete all keys')
    r.flushall()
    assert len(r.keys()) == 0

    _log('Adding a key')
    key = 'thing'
    value = 'deathray'
    r.set(key, value)

    _log('Getting that key')
    gotten_value = r.get(key)

    _log('Do they match?')
    assert gotten_value == value
    _log('They match!')

    _log('Playing with append')
    r.append(key, value)
    gotten_value = r.get(key)
    assert gotten_value == value * 2

    _log('Trying out client_setname')
    name = 'Reina'
    r.client_setname(name)

    _log('Playing with client_getname')
    getname = r.client_getname()
    _log(getname)
    assert getname == name

    _log('What\'s config_get?')
    configget = r.config_get()
    _log('Oh, it\'s', configget)

    _log('And client_list?')
    client_list = r.client_list()
    _log('It is this', client_list)

    _log('Some "info" now')
    info = r.info()
    _log('The "info" is', info)

    _log('Add a bunch of stuff!')
    for i in xrange(10000):
        r.set(i, i)

def from_url():
    # This returns the exact same object type as just redis.StrictRedis, it's
    # just a different way of grabbing it
    r = redis.StrictRedis.from_url('redis://%s/0' % REDIS_HOST)

    _log('Pinging this one too')
    r.ping()
    _log('Pinged')

def multi_db():
    r0 = redis.StrictRedis(host=REDIS_HOST, db=0)
    r1 = redis.StrictRedis(host=REDIS_HOST, db=1)

    assert r0 != r1
    assert r0.dbsize() != r1.dbsize()

    _log('The r0 client is the first one, it should have 10001 keys')
    assert r0.dbsize() == 10001

    _log('But the r1 client is new, it should have 0 keys')
    assert r1.dbsize() == 0

def connection():
    c = redis.Connection(host=REDIS_HOST)
    _log('The type of redis.Connection is', type(c), 'which makes sense')

    c.disconnect()
    c.connect()

@newrelic.agent.function_trace()
def use_it():
    r = redis.StrictRedis(host=REDIS_HOST, db=0)
    max_num = 10**2

    _log('Find some prime numbers')

    num = random.randint(1, max_num)
    _log('Testing', num)
    cnt = 1
    while not is_prime(num, r):
        num = random.randint(1, max_num)
        _log('Testing', num)
        cnt += 1
    _log(num, 'is prime!!')

    _log('Tried', cnt, 'numbers')
    _log('There are', r.dbsize(), 'keys in the db')

@newrelic.agent.function_trace()
def is_prime(num, r=None):
    if r:
        if r.exists(num):
            _log('Using cached value')
            cached_str_value = r.get(num)
            cached_value = cached_str_value == 'True'
            return cached_value

    if num <= 1:
        value = False
    elif num == 2:
        value = True
    elif num % 2 == 0:
        value = False
    else:
        for i in xrange(3, int(num ** 0.5 + 1), 2):
            if num % i == 0:
                value = False
                break
        else:
            value = True

    if r:
        _log('Adding key to the cache')
        r.set(num, value)

    return value

def change_db():
    # Despite changing databases this still works because there is only one
    # Connection object in the connection pool. If a different Connection is
    # used for each of these calls, the assertions would fail. A particular
    # Connection will save the db, but it will not share that context with
    # other Connections in the pool.
    r = redis.Redis(host=REDIS_HOST, db=0)
    r.flushall()

    num_keys_1 = 1000
    num_keys_2 = 20

    _log('Selecting db 1')
    rv = r.execute_command('SELECT 1')
    _log('Response', rv)

    _log('Adding stuff to it')
    for i in xrange(num_keys_1):
        r.set(i, i)

    _log('Save number of keys')
    size_1 = r.dbsize()
    _log('There are', size_1, 'keys')
    assert size_1 == num_keys_1

    _log('Selecting db 2')
    rv = r.execute_command('SELECT 2')
    _log('Response', rv)

    _log('Adding stuff to it')
    for i in xrange(num_keys_2):
        r.set(i, i)

    _log('Save number of keys')
    size_2 = r.dbsize()
    _log('There are', size_2, 'keys')
    assert size_2 == num_keys_2

    assert size_1 != size_2

def simple():
    r = redis.StrictRedis(host=REDIS_HOST)

    _log('Flushing all databases')
    r.flushall()

    key = 'dog'
    value = 'cat'

    _log('Setting key', key, 'to value', value)
    r.set(key, value)
    _log('Getting key', key)
    get_value = r.get(key)
    _log('Key', key, 'was set to', get_value)

    assert get_value == value

def execute_command():
    assert redis.VERSION == (2, 9, 1)

    r = redis.StrictRedis(host=REDIS_HOST)
    _log(r.execute_command('CLIENT', 'LIST', parse='LIST'))

def default_port():
    r = redis.StrictRedis.from_url('redis://localhost:6379')
    _log('What did it say about the port?',
            r.connection_pool.connection_kwargs)
    _log('Getting something')
    r.get('something')

def sockets():
    _log('Trying a regular socket')
    r = redis.StrictRedis.from_url('unix:///tmp/redis.sock')
    try:
        r.get('hello')
    except:
        _log('Nope!')
    else:
        _log('Yup!')

    _log('What about weird sockets')
    r = redis.StrictRedis.from_url('unix:///tmp/redis.sock?smellysocks=1')
    try:
        r.get('hello')
    except:
        _log('Nope!')
    else:
        _log('Yup!')

def client_list():
    client = redis.StrictRedis(host=REDIS_HOST)
    _log(client.execute_command('CLIENT', 'LIST', parse='LIST'))

def db_None():
    client = redis.StrictRedis()

    try:
        _log(client.connection_pool.connection_kwargs)
        _log(client.execute_command('CLIENT', 'LIST', parse='LIST'))
    except:
        _log('FAIL!')
        raise
    else:
        _log('SUCCESS!')

def main():
    _log('What happens if something is None?')
    db_None()

if __name__ == '__main__':
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'redis'):
        main()
