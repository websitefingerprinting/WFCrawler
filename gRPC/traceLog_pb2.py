# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: traceLog.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='traceLog.proto',
  package='pb',
  syntax='proto3',
  serialized_options=b'Z8github.com/websitefingerprinting/wfdef.git/transports/pb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0etraceLog.proto\x12\x02pb\x1a\x1bgoogle/protobuf/empty.proto\"-\n\tSignalMsg\x12\x0e\n\x06turnOn\x18\x01 \x01(\x08\x12\x10\n\x08\x66ilePath\x18\x02 \x01(\t2G\n\x0cTraceLogging\x12\x37\n\x0cSignalLogger\x12\r.pb.SignalMsg\x1a\x16.google.protobuf.Empty\"\x00\x42:Z8github.com/websitefingerprinting/wfdef.git/transports/pbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_SIGNALMSG = _descriptor.Descriptor(
  name='SignalMsg',
  full_name='pb.SignalMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='turnOn', full_name='pb.SignalMsg.turnOn', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filePath', full_name='pb.SignalMsg.filePath', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=51,
  serialized_end=96,
)

DESCRIPTOR.message_types_by_name['SignalMsg'] = _SIGNALMSG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SignalMsg = _reflection.GeneratedProtocolMessageType('SignalMsg', (_message.Message,), {
  'DESCRIPTOR' : _SIGNALMSG,
  '__module__' : 'traceLog_pb2'
  # @@protoc_insertion_point(class_scope:pb.SignalMsg)
  })
_sym_db.RegisterMessage(SignalMsg)


DESCRIPTOR._options = None

_TRACELOGGING = _descriptor.ServiceDescriptor(
  name='TraceLogging',
  full_name='pb.TraceLogging',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=98,
  serialized_end=169,
  methods=[
  _descriptor.MethodDescriptor(
    name='SignalLogger',
    full_name='pb.TraceLogging.SignalLogger',
    index=0,
    containing_service=None,
    input_type=_SIGNALMSG,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_TRACELOGGING)

DESCRIPTOR.services_by_name['TraceLogging'] = _TRACELOGGING

# @@protoc_insertion_point(module_scope)