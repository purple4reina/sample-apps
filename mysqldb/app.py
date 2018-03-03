import os
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import MySQLdb

DBUSER = 'python_agent'
DOCKER_HOST = os.environ.get('DOCKER_HOST')
if DOCKER_HOST:
    DOCKER_HOST = DOCKER_HOST.lstrip('tcp:/').split(':', 1)[0]


def _create_table():
    db = MySQLdb.connect(db=DBUSER, user=DBUSER, passwd=DBUSER,
            host=DOCKER_HOST)
    cur = db.cursor()
    cur.execute('DROP TABLE people')
    cur.execute('CREATE TABLE people (name text, ssn text)')
    cur.close()
    db.commit()
    db.close()


@newrelic.agent.background_task()
def main():
    # docker run -d -p 5432:5432 --network="bridge" postgresql
    db = MySQLdb.connect(db=DBUSER, user=DBUSER, passwd=DBUSER,
            host=DOCKER_HOST)
    cur = db.cursor()
    cur.executemany(
            """
             SELECT name, ssn FROM people;
             INSERT INTO people (name, ssn) VALUES (%s, %s);
            """, [('Jane Doe', '123-45-6789',)])
    cur.close()
    db.commit()
    db.close()


if __name__ == '__main__':
    print('----------------------------------------')
    _create_table()
    main()
    print('----------------------------------------')
