from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()

def print_gevent_version():
    import gevent
    v = gevent.version_info
    print('gevent version:  %s.%s.%s' % (v.major, v.minor, v.micro))

print_gevent_version()

from newrelic.core.data_collector import send_request

def direct():
    session = None
    url = 'https://collector.newrelic.com/agent_listener/invoke_raw_method'
    method = 'get_redirect_host'
    license_key = 'f429aaa8f9c1687093c9bd211ef189b75952bf42'
    agent_run_id = None
    payload = ()

    resp = send_request(session, url, method, license_key, agent_run_id, payload)
    print(resp)

if __name__ == '__main__':
    direct()

    import newrelic.agent
    newrelic.agent.initialize('newrelic.ini')
    app = newrelic.agent.register_application(timeout=10.0)
    import requests
    with newrelic.agent.BackgroundTask(app, 'Background'):
        requests.get('http://example.com')
