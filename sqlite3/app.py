import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10)

import sqlite3
import time


@newrelic.agent.background_task()
def main():
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
            print('row: ', row)

        conn.commit()


if __name__ == '__main__':
    print('----------------------------------------')
    main()
    print('----------------------------------------')
