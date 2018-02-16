import os
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import psycopg2

DBUSER = 'python_agent'
DOCKER_HOST = os.environ.get('DOCKER_HOST')
if DOCKER_HOST:
    DOCKER_HOST = DOCKER_HOST.lstrip('tcp:/').split(':', 1)[0]


def _create_table(cur):
    cur.execute('DROP TABLE people')
    cur.execute('CREATE TABLE people (name text, number bigint)')


@newrelic.agent.background_task()
def main():
    # docker run -d -p 5432:5432 --network="bridge" postgresql
    with psycopg2.connect(
            database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST) as conn:
        cur = conn.cursor()
        _create_table(cur)
        cur.execute(
                'INSERT INTO people (name, number) VALUES (%s, %s)',
                ['Jane Doe', 123456789000000])
        cur.execute('SELECT * FROM people')
        for record in cur:
            print('record: ', record)


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
