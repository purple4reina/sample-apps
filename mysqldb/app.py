import newrelic.agent
newrelic.agent.initialize('/data/newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import MySQLdb
import random

PYAGENT = 'python_agent'

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def instance_info():
    with MySQLdb.connect(
            host='mysql',
            user=PYAGENT,
            passwd=PYAGENT,
            db='') as connection:
        pass

def main():
    _log('MySQLdb anyone?')
    instance_info()

if __name__ == '__main__':
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'mysql'):
        main()
