"""
Host ViewSet module.
"""

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action

from core.models import Host
from rest.permissions import IsOwnerOrForbidden, HostPermission
from rest.serializers import HostCreationSerializer, PluginSerializer


class HostViewSet(viewsets.ModelViewSet):
    """
    Host endpoint, availaible for all users. It filters Hosts by user
    and only display data for host in same the group of user.
    """
    model = Host
    permission_classes = (HostPermission,)

    def get_queryset(self):
        return self.model.objects.user_filter(self.request.user)

    def create(self, request):
        serializer = HostCreationSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(JSONRenderer().render(serializer.data),
                    status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    @action(permission_classes=[IsOwnerOrForbidden])
    def create_plugins(self, request, pk=None):
        host = self.get_object()
        plugins = host.create_plugins(request.DATA.get('plugins',[]))
        if plugins:
            serializer = PluginSerializer(plugins, many=True)
            return Response(serializer.data,
                    status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_204_NO_CONTENT)

