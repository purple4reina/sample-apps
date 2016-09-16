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

if __name__ == '__main__':
    app.run(debug=True)
