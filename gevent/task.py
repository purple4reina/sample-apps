def agent():
    import os
    import newrelic.agent
    newrelic.agent.initialize(os.environ.get('NEW_RELIC_CONFIG_FILE'))
    newrelic.agent.register_application(timeout=10.0)

def gevent():
    import gevent.monkey
    print('--------------------monkey--------------------')
    gevent.monkey.patch_ssl()
    print('--------------------monkey--------------------')

def wait():
    while True:
        pass

agent()
gevent()

# FAIL: agent(); gevent()
# PASS: gevent(); agent()
