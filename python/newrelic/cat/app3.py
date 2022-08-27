import flask
import requests
import sqlite3
import time

app3 = flask.Flask('app3')

def _execute_db():
    with sqlite3.connect('sqlite3.db') as conn:
        c = conn.cursor()

        try:
            c.execute('CREATE TABLE stocks'
                    '(date text, trans text, symbol text, qty real, price real)')
        except sqlite3.OperationalError:
            pass

        c.execute('INSERT INTO stocks VALUES'
                '("2006-01-05","BUY","NEWR",100,%s)' % time.time())

        for row in c.execute('SELECT * FROM stocks WHERE trans="BUY"'):
            pass

        conn.commit()


@app3.route('/')
def app3_home():
    _execute_db()
    return '*'

if __name__ == '__main__':
    app3.run(debug=True, port=5002)
