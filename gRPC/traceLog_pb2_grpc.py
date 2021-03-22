# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import traceLog_pb2 as traceLog__pb2


class TraceLoggingStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SignalLogger = channel.unary_unary(
                '/pb.TraceLogging/SignalLogger',
                request_serializer=traceLog__pb2.SignalMsg.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class TraceLoggingServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SignalLogger(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TraceLoggingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SignalLogger': grpc.unary_unary_rpc_method_handler(
                    servicer.SignalLogger,
                    request_deserializer=traceLog__pb2.SignalMsg.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.TraceLogging', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TraceLogging(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SignalLogger(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/pb.TraceLogging/SignalLogger',
            traceLog__pb2.SignalMsg.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)