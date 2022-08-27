import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.register_application(timeout=10.0)

import sys
sys.path.append('..')

from utils.decorators import print_metrics

import time
import pika


@print_metrics()
@newrelic.agent.background_task()
def main():
    with pika.BlockingConnection(
            pika.ConnectionParameters('localhost')) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='hello')

        body = 'seconds since epoch %s' % time.time()
        channel.basic_publish(
            exchange='',
            routing_key='hello',
            body=body,
        )


if __name__ == '__main__':
    print '===================================='
    main()
    print '===================================='
