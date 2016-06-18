from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from dumbapp.models import Dumbo
from dumbapp.serializers import DumboSerializer

import toxiproxy_controller


class BaseAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = DumboSerializer(
            data={'name': Dumbo.create_name()}
        )

        if serializer.is_valid():
            if kwargs.get('latency'):
                with self.toxic(kwargs.get('latency')):
                    serializer.save()
            else:
                with self.toxic():
                    serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# no toxics
class CreateDumbo(BaseAPIView):

    def __init__(self):
        self.toxic = toxiproxy_controller.NoToxic


# cut connection to mysql server
class GoAwayDumbo(BaseAPIView):

    def __init__(self):
        self.toxic = toxiproxy_controller.NoMySqlServer


# with latency
class LatencyConnection(BaseAPIView):

    def __init__(self):
        self.toxic = toxiproxy_controller.MySqlLatency


class BaseNoSerializer(APIView):

    def post(self, request, *args, **kwargs):
        latency = kwargs.get('latency')

        if latency:
            with self.toxic(latency):
                Dumbo.objects.create(name=Dumbo.create_name())
        else:
            with self.toxic():
                Dumbo.objects.create(name=Dumbo.create_name())

        return Response('OK')


# no toxics
class NoSerializer(BaseNoSerializer):

        def __init__(self):
            self.toxic = toxiproxy_controller.NoToxic


# cut connection to mysql server
class GoAwayDumboNoSerializer(BaseNoSerializer):

    def __init__(self):
        self.toxic = toxiproxy_controller.NoMySqlServer


# with latency
class LatencyConnectionNoSerializer(BaseNoSerializer):

    def __init__(self):
        self.toxic = toxiproxy_controller.MySqlLatency
