# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import route_guide_pb2 as route__guide__pb2


class RouteGuideStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetFeature = channel.unary_unary(
        '/RouteGuide/GetFeature',
        request_serializer=route__guide__pb2.Point.SerializeToString,
        response_deserializer=route__guide__pb2.Feature.FromString,
        )


class RouteGuideServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetFeature(self, request, context):
    """Obtains the feature at a given position.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RouteGuideServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetFeature': grpc.unary_unary_rpc_method_handler(
          servicer.GetFeature,
          request_deserializer=route__guide__pb2.Point.FromString,
          response_serializer=route__guide__pb2.Feature.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'RouteGuide', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
