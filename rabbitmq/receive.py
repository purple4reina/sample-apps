import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.register_application(timeout=10.0)

import sys
sys.path.append('..')

from utils.decorators import print_nice_transaction_trace, print_metrics

import pika


def main():

    def callback(ch, method, properties, body):
        print 'received: ', body
        print 'headers: ', properties.headers

    with pika.BlockingConnection(
            pika.ConnectionParameters('localhost')) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        channel.basic_consume(callback, queue='hello', no_ack=True)
        channel.start_consuming()


if __name__ == '__main__':
    print '===================================='
    main()
    print '===================================='
