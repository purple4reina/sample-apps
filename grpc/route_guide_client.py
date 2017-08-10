import grpc

import route_guide_pb2
import route_guide_pb2_grpc


def send():
    channel = grpc.insecure_channel('localhost:50051')
    stub = route_guide_pb2_grpc.RouteGuideStub(channel)
    feature = stub.GetFeature(route_guide_pb2.Point(latitude=409146138,
        longitude=-746188906))
    print 'feature.name: ', feature.name


if __name__ == '__main__':
    send()
