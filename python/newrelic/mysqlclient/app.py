import time
time.sleep(10)  # give mysql container time to start up

import newrelic.agent
newrelic.agent.initialize('/data/newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import MySQLdb


@newrelic.agent.background_task()
def main():
    with MySQLdb.connect(user='root', host='mysql', password='password') as cur:
        try:
            cur.execute('DROP DATABASE my_database')
        except:
            pass
        finally:
            cur.execute('CREATE DATABASE my_database')

    with MySQLdb.connect(user='root', host='mysql', password='password',
            database='my_database') as cur:
        cur.execute('CREATE TABLE my_table (name VARCHAR(20))')
        print cur.execute('SELECT * FROM my_table')


if __name__ == '__main__':
    print '----------------------------------------'
    main()
    print '----------------------------------------'
