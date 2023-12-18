import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10)

import random

from route_guide_pb2 import Point
from utils.decorators import print_metrics


@print_metrics()
@newrelic.agent.background_task()
def main():
    point = Point(
        latitude=random.randint(-100, 100),
        longitude=random.randint(-100, 100))

    serialized = point.SerializeToString()
    deserialized = point.FromString(serialized)
    assert deserialized == point
    print 'deserialized: ', deserialized


if __name__ == '__main__':
    print '----------------------------------------'
    main()
    print '----------------------------------------'
