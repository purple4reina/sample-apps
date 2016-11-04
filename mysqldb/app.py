import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import MySQLdb
import random

PYAGENT = 'python_agent'

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def instance_info():
    with MySQLdb.connect(
            user=PYAGENT,
            passwd=PYAGENT,
            db=PYAGENT) as cursor:

        cursor.execute("""drop table if exists datastore_mysqldb""")
        cursor.execute("""create table datastore_mysqldb """
                """(a integer, b real, c text)""")

def main():
    _log('MySQLdb anyone?')
    instance_info()

if __name__ == '__main__':
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'mysql'):
        main()
