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
    cur.execute('CREATE TABLE people (name text, ssn text)')


@newrelic.agent.background_task()
def main():
    # docker run -d -p 5432:5432 --network="bridge" postgresql
    with psycopg2.connect(database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST) as conn:
        cur = conn.cursor()
        cur.execute(
                """
                 INSERT INTO people (name, ssn) VALUES (%s, %s);
                 INSERT INTO people (name, ssn) VALUES (%s, %s);
                 COMMIT;
                 SELECT (name, ssn) FROM people
                """, ['Jane Doe', '123-45-6789']+['Jane Doe', '123-45-6789'])
        print(cur.fetchall())


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
