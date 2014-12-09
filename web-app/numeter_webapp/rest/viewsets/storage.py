"""
Storage ViewSet module.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.decorators import action

from core.models import Storage
from rest.serializers import StorageSerializer, HostSerializer
from rest.views import ModelListDelete


class StorageViewSet(ModelListDelete, viewsets.ModelViewSet):
    """
    User endpoint, only available for superusers.
    """
    model = Storage
    serializer_class = StorageSerializer
    allowed_methods = ('GET', 'PATCH', 'DELETE', 'POST')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.web_filter(q)

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
