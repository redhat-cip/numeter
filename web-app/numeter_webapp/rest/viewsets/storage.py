"""
Storage ViewSet module.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.decorators import action

from core.models import Storage
from rest.serializers import HostSerializer


class StorageViewSet(viewsets.ModelViewSet):
    """
    User endpoint, only available for superusers.
    """
    model = Storage

    @action()
    def create_hosts(self, request, pk=None):
        storage = self.get_object()
        hosts = storage.create_hosts(request.DATA.get('hosts', []))
        if hosts:
            serializer = HostSerializer(hosts, many=True)
            return Response(serializer.data,
                    status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_204_NO_CONTENT)
