# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: route_guide.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='route_guide.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x11route_guide.proto\",\n\x05Point\x12\x10\n\x08latitude\x18\x01 \x01(\x05\x12\x11\n\tlongitude\x18\x02 \x01(\x05\"\x17\n\x07\x46\x65\x61ture\x12\x0c\n\x04name\x18\x01 \x01(\t2.\n\nRouteGuide\x12 \n\nGetFeature\x12\x06.Point\x1a\x08.Feature\"\x00\x62\x06proto3')
)




_POINT = _descriptor.Descriptor(
  name='Point',
  full_name='Point',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='latitude', full_name='Point.latitude', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='longitude', full_name='Point.longitude', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=65,
)


_FEATURE = _descriptor.Descriptor(
  name='Feature',
  full_name='Feature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Feature.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=67,
  serialized_end=90,
)

DESCRIPTOR.message_types_by_name['Point'] = _POINT
DESCRIPTOR.message_types_by_name['Feature'] = _FEATURE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Point = _reflection.GeneratedProtocolMessageType('Point', (_message.Message,), dict(
  DESCRIPTOR = _POINT,
  __module__ = 'route_guide_pb2'
  # @@protoc_insertion_point(class_scope:Point)
  ))
_sym_db.RegisterMessage(Point)

Feature = _reflection.GeneratedProtocolMessageType('Feature', (_message.Message,), dict(
  DESCRIPTOR = _FEATURE,
  __module__ = 'route_guide_pb2'
  # @@protoc_insertion_point(class_scope:Feature)
  ))
_sym_db.RegisterMessage(Feature)


try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities


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
          request_serializer=Point.SerializeToString,
          response_deserializer=Feature.FromString,
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
            request_deserializer=Point.FromString,
            response_serializer=Feature.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'RouteGuide', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaRouteGuideServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    # missing associated documentation comment in .proto file
    pass
    def GetFeature(self, request, context):
      """Obtains the feature at a given position.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaRouteGuideStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    # missing associated documentation comment in .proto file
    pass
    def GetFeature(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Obtains the feature at a given position.
      """
      raise NotImplementedError()
    GetFeature.future = None


  def beta_create_RouteGuide_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('RouteGuide', 'GetFeature'): Point.FromString,
    }
    response_serializers = {
      ('RouteGuide', 'GetFeature'): Feature.SerializeToString,
    }
    method_implementations = {
      ('RouteGuide', 'GetFeature'): face_utilities.unary_unary_inline(servicer.GetFeature),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_RouteGuide_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('RouteGuide', 'GetFeature'): Point.SerializeToString,
    }
    response_deserializers = {
      ('RouteGuide', 'GetFeature'): Feature.FromString,
    }
    cardinalities = {
      'GetFeature': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'RouteGuide', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)
