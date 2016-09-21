import flask
import os
import psycopg2
import sqlite3
import time

app = flask.Flask(__name__)

DBUSER = 'python_agent'
DOCKER_HOST = os.environ.get('DOCKER_HOST')
if DOCKER_HOST:
    DOCKER_HOST = DOCKER_HOST.lstrip('tcp:/').split(':', 1)[0]

@app.route('/')
def home():
    return ''

@app.route('/sqlite3')
def sqlite():
    with sqlite3.connect('sqlite3-a.db') as conn:
        c = conn.cursor()
        _create_db(c)
        _insert_db(c)
        conn.commit()

    with sqlite3.connect('sqlite3-b.db') as conn:
        c = conn.cursor()
        _create_db(c)
        _insert_db(c)
        conn.commit()

    return ''

@app.route('/psycopg2')
def psycopg():
    with psycopg2.connect(
            database='rabolofia', user='rabolofia', password='') as conn:
        with conn.cursor() as c:
            _create_db(c, conn=conn)
            _insert_db(c)
            conn.commit()

    with psycopg2.connect(
            database='rabolofia', user='rabolofia', password='') as conn:
        with conn.cursor() as c:
            _create_db(c, conn=conn)
            _insert_db(c)
            conn.commit()

    return ''

def _insert_db(c):
    number = str(time.time()).replace('.', '')[:-11:-1]
    try:
        c.execute("""
            INSERT INTO people VALUES
                ('John','Doe',%s),
                ('Jane','Doe',%s)
        """, (number, number))
    except sqlite3.OperationalError:
        c.execute("""
            INSERT INTO people VALUES
                ('John','Doe',?),
                ('Jane','Doe',?)
        """, (number, number))

def _create_db(c, conn=None):
    try:
        c.execute("""
            CREATE TABLE people
                (first text, last text, number text)
        """)
    except sqlite3.OperationalError:
        pass
    except psycopg2.ProgrammingError:
        conn.rollback()

@app.route('/pg-port')
def pg_port():
    # connect to postgresql through a different port
    # start db with:
    #   `docker run -d --name packnsend-postgresql -p 5433:5432 --network="bridge" postgresql`
    with psycopg2.connect(
            database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST) as conn:
        pass
    return ''

@app.route('/all')
def test_all_types():
    # (1)
    # docker host, default port
    #   docker run -d -p 5432:5432 --network="bridge" postgresql
    #   ('192.168.99.100', None) -> ('192.168.99.100', '5432')
    with psycopg2.connect(
            database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST) as conn:
        pass

    # (2)
    # docker host, port 5433
    #   docker run -d -p 5433:5432 --network="bridge" postgresql
    #   ('192.168.99.100', '5433') -> ('192.168.99.100', '5433')
    with psycopg2.connect(
            database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST, port=5433) as conn:
        pass

    # (3)
    # docker host, port 5432
    #   reuse (1)
    #   ('192.168.99.100', '5432') -> ('192.168.99.100', '5432')
    with psycopg2.connect(
            database=DBUSER, user=DBUSER, password=DBUSER,
            host=DOCKER_HOST, port=5432) as conn:
        pass

    # (4)
    # localhost, port 5432
    #   already ready already
    #   ('localhost', '5432') -> ('localhost', '5432')
    with psycopg2.connect(
            database='rabolofia', user='rabolofia', password='rabolofia',
            host='localhost', port=5432) as conn:
        pass

    # (5)
    # localhost, port 5433
    #   `echo "
    #   rdr pass on lo0 inet proto tcp from any to any port 5433 -> 127.0.0.1 port 5432
    #   " | sudo pfctl -ef -` # forward ports
    #   ('localhost', '5433') -> ('localhost', '5433')
    with psycopg2.connect(
            database='rabolofia', user='rabolofia', password='rabolofia',
            host='localhost', port=5433) as conn:
        pass

    # (6)
    # ::1, default port
    #   already ready already
    #   ('::1', None) -> ('::1', '5432')
    with psycopg2.connect(
            database='rabolofia', user='rabolofia', password='rabolofia',
            host='::1') as conn:
        pass

    # (7)
    # localhost, port 5432 using string things
    #   already ready already
    #   ('localhost', '5433') -> ('localhost', '5433')
    with psycopg2.connect('host=localhost port=5433') as conn:
        pass


    # (8)
    # uri, localhost, default port
    #   already ready already
    #   not yet working on this branch
    with psycopg2.connect('postgres://localhost') as conn:
        pass

    return ''

@app.route('/socket')
def socket():
    # localhost, socket
    # This totally isn't working so I'm giving up
    with psycopg2.connect(
            database='root', user='root', password='root') as conn:
        pass

    return ''


if __name__ == '__main__':
    app.run(debug=True)
