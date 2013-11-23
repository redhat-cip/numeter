"""
Host ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.decorators import action

from core.models import Host
from rest.permissions import IsOwnerOrForbidden, HostPermission
from rest.serializers import HostSerializer, HostCreationSerializer, PluginSerializer
from rest.views import ModelListDelete


class HostViewSet(ModelListDelete, ModelViewSet):
    """
    Host endpoint, availaible for all users. It filters Hosts by user
    and only display data for host in same the group of user.
    """
    model = Host
    permission_classes = (HostPermission,)
    serializer_class = HostSerializer
    allowed_methods = ('POST', 'PATCH', 'DELETE', 'GET')

    @action(permission_classes=[IsOwnerOrForbidden])
    def create_plugins(self, request, pk=None):
        host = self.get_object()
        plugins = host.create_plugins(request.DATA.get('plugins', []))
        if plugins:
            serializer = PluginSerializer(plugins, many=True)
            return Response(serializer.data,
                    status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_204_NO_CONTENT)

    def create(self, request):
        serializer = HostCreationSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(JSONRenderer().render(serializer.data),
                            status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                        status=HTTP_400_BAD_REQUEST)
