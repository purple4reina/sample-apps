import flask
import psycopg2
import sqlite3
import time

app = flask.Flask(__name__)

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
    c.execute("""
        INSERT INTO people VALUES
            ('John','Doe',%s),
            ('Jane','Doe',%s)
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

if __name__ == '__main__':
    app.run(debug=True)
