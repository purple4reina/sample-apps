import grpc
import time

from concurrent import futures

import route_guide_pb2
import route_guide_pb2_grpc


# RouteGuideServicer provides an implementation of the methods of the
# RouteGuide service.
class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):

    def GetFeature(self, request, context):
        print 'Got feature request: %s' % id(request)
        return route_guide_pb2.Feature(name='hello world')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
        RouteGuideServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    while True:
        time.sleep(10)


if __name__ == '__main__':
    serve()
