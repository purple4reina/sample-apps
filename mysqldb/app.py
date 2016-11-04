import newrelic.agent
newrelic.agent.initialize('/data/newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import MySQLdb
import random

PYAGENT = 'python_agent'

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def instance_info():
    kwargs = dict(
        host='mysql',
        user=PYAGENT,
        passwd=PYAGENT,
        db=PYAGENT,
    )

    try:
        with MySQLdb.connect(**kwargs) as cursor:

            cursor.execute("""drop table if exists datastore_mysqldb""")
            cursor.execute("""create table datastore_mysqldb """
                    """(a integer, b real, c text)""")
    except:
        _log('Something went wrong!')
        raise
    else:
        _log('Success!')

def main():
    _log('MySQLdb anyone?')
    instance_info()

if __name__ == '__main__':
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'mysql'):
        main()
