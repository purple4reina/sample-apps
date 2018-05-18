import sys
sys.path.insert(0, 'mymodule.zip')

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import mymodule


@newrelic.agent.background_task()
def main():
    resp = mymodule.fetch('http://example.com')
    assert resp.status_code == 200


if __name__ == '__main__':
    main()
