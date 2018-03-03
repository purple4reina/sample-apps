import newrelic
import newrelic.agent
newrelic.agent.initialize('/data/newrelic.ini')
APP = newrelic.agent.register_application(timeout=10.0)

import MySQLdb
import random

PYAGENT = 'python_agent'

def _log(*msg):
    print '-' * random.randint(1, 10) + '> ' + ' '.join(map(str, msg))

def _exercise_db(cursor):
    cursor.execute("""drop table if exists datastore_mysqldb""")
    cursor.execute("""create table datastore_mysqldb """
            """(a integer, b real, c text)""")

def instance_info():
    kwargs = dict(
        user=PYAGENT,
        passwd=PYAGENT,
        db=PYAGENT,
    )

    _log('MySQL host "mysql_one"')
    with MySQLdb.connect(host='mysql_one', **kwargs) as cursor:
        _exercise_db(cursor)

    _log('MySQL host "mysql_two"')
    with MySQLdb.connect(host='mysql_two', **kwargs) as cursor:
        _exercise_db(cursor)

def main():
    _log('MySQLdb anyone?')
    instance_info()

if __name__ == '__main__':
    _log('Using agent version', newrelic.version)
    with newrelic.agent.BackgroundTask(APP, 'mysql'):
        main()
