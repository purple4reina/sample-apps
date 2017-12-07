import newrelic.agent as nr

import flask
import redis
import requests
import sqlite3

app = flask.Flask(__name__)


@app.route('/')
def index():
    txn = nr.current_transaction()
    if txn:
        for attr in txn.agent_attributes:
            print('attr: ', attr)
        print('txn._request_uri: ', txn._request_uri)
    print('flask.request.headers:\n', flask.request.headers)
    return '*'


@app.route('/sql')
def sql():
    with sqlite3.connect(':memory:') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE stocks'
                '(date text, trans text, symbol text, qty real, price real)')

        # the quoting style determines if we correctly obfuscate!
        c.execute('INSERT INTO stocks VALUES'
                #'("2006-01-05","BUY","NEWR",100,35.14)')
                "('2006-01-05','BUY','NEWR',100,35.14)")

        c.execute('SELECT * FROM stocks WHERE trans="BUY"')
        conn.commit()
    return '*'


@app.route('/message')
def message():
    txn = nr.current_transaction()
    params = {'hello': 'world'}
    with nr.MessageTrace(txn, library='RabbitMQ', operation='Consume',
            destination_type='Exchange', destination_name='x',
            params=params) as mt:
        print('mt.params: ', mt.params)
    return '*'


@app.route('/error')
def error():
    assert False, 'Here is the error message'


@app.route('/event')
def record_custom_event():
    event_type = 'Rey-Event'
    params = {'hello': 'event'}
    txn = nr.current_transaction()
    txn.settings.custom_insights_events.enabled = True
    nr.record_custom_event(event_type, params)
    return '*'


@app.route('/param')
def add_custom_parameter():
    nr.add_custom_parameter('hello', 'world')
    return '*'


@app.route('/capture')
def capture_request_params():
    nr.capture_request_params()
    transaction = nr.current_transaction()
    transaction.capture_params = True
    return '*'


@app.route('/except')
def notice_error():
    try:
        raise Exception('hello world')
    except:
        nr.record_exception(params={'hello': 'world'})
    return '*'


@app.route('/redis')
def redis_trace():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(r.set('hello', 'world'))
    print(r.get('hello'))
    return '*'


if __name__ == '__main__':
    app.run(debug=True)
