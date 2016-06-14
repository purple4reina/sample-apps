import os
import sys
import toxiproxy

import django.db

DOCKER_IP = os.environ.get(
    'DOCKER_HOST', 'localhost').strip('tcp://').split(':')[0]
PROXY_NAME = 'mysql_proxy'
TOXIC_NAME = 'mysql_toxic'
TIMEOUT = 10  # seconds
LATENCY = 1000  # milliseconds


def get_toxiproxy_server():
    tp = toxiproxy.Toxiproxy(server_host=DOCKER_IP)
    assert tp.running()

    try:
        tp.create(
            DOCKER_IP + ':3306',
            PROXY_NAME,
            listen=':33306',
            enabled=True,
        )
    except toxiproxy.exceptions.ProxyExists:
        pass

    return tp


def enable_timeout(timeout=TIMEOUT):
    tp = get_toxiproxy_server()
    api = tp.api_server

    new_toxic = {
        'name': TOXIC_NAME,
        'type': 'timeout',
        'attributes': {
            'timeout': TIMEOUT,
        },
    }
    try:
        resp = api.post(
            '/proxies/%s/toxics' % PROXY_NAME,
            json=new_toxic,
        )
    except toxiproxy.exceptions.ProxyExists:
        print 'toxic already exists... updating it...'
        resp = api.post(
            '/proxies/%s/toxics/%s' % (PROXY_NAME, TOXIC_NAME),
            json=new_toxic,
        )
    print 'toxic created: %s' % resp.json()


def enable_latency(latency=LATENCY):
    try:
        latency = int(latency)
    except ValueError:
        print 'could not read latency given, sorry!'
        latency = LATENCY

    tp = get_toxiproxy_server()
    api = tp.api_server

    new_toxic = {
        'name': TOXIC_NAME,
        'type': 'latency',
        'attributes': {
            'latency': latency,
        },
    }

    tp.reset()
    resp = api.post(
        '/proxies/%s/toxics' % PROXY_NAME,
        json=new_toxic,
    )
    print 'toxic created: %s' % resp.json()


def stop_toxiproxies():
    tp = get_toxiproxy_server()
    tp.reset()
    print 'all toxics stopped!'


def get_toxic():
    tp = get_toxiproxy_server()
    api = tp.api_server
    try:
        resp = api.get(
            '/proxies/%s/toxics/%s' % (PROXY_NAME, TOXIC_NAME),
        )
        return resp.json()
    except:
        return


def stop_mysql():
    """
    disabling the proxy should then also "bring down" the mysql server
    """
    tp = get_toxiproxy_server()
    api = tp.api_server

    tp.reset()

    disable = {
        'enabled': False,
    }

    print 'stopping connections to mysql server...'
    api.post(
        '/proxies/%s' % PROXY_NAME,
        json=disable,
    )


class NoMySqlServer(object):

    def __enter__(self):
        dbwrapper = django.db.connections['default']
        dbwrapper.connect()

        # cut the connection between django and the mysql server
        stop_mysql()

        # for some reason this is required
        dbwrapper.is_usable()

    def __exit__(self, *args, **kwargs):
        stop_toxiproxies()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'stop':
        stop_toxiproxies()
    elif len(sys.argv) == 3 and sys.argv[1] == 'start':
        enable_latency(sys.argv[2])
    else:
        enable_latency()
