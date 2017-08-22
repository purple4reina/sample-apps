import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.register_application(timeout=10)

import grpc
import random

import route_guide_pb2
import route_guide_pb2_grpc


@newrelic.agent.background_task()
def send():
    channel = grpc.insecure_channel('localhost:50051')
    stub = route_guide_pb2_grpc.RouteGuideStub(channel)
    feature = stub.GetFeature(route_guide_pb2.Point(
            latitude=random.randint(-100, 100),
            longitude=random.randint(-100, 100)))
    print 'feature.name: ', feature.name


if __name__ == '__main__':
    print '----------------------------------------'
    send()
    print '----------------------------------------'
