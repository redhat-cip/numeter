"""
Plugin ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet 
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from core.models import Plugin
from rest.permissions import IsOwnerOrForbidden
from rest.serializers import PluginSerializer, SourceSerializer
from rest.views import ModelListDelete


class PluginViewSet(ModelListDelete, ModelViewSet):
    """
    Plugin endpoint, availaible for all users. It filters Plugins by user
    and only display data for plugin in same the group of user.
    """
    model = Plugin
    permission_classes = (IsOwnerOrForbidden,)
    allowed_methods = ('GET', 'PATCH', 'DELETE')
    serializer_class = PluginSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        if self.request.method != 'GET':
            return self.model.objects.user_web_filter(q, self.request.user)
        return self.model.objects.user_filter(self.request.user)

    @detail_route(permission_classes=[IsOwnerOrForbidden], allowed_methods=['POST'])
    def create_sources(self, request, pk=None):
        plugin = self.get_object()
        sources = plugin.create_data_sources(request.DATA.get('sources',[]))
        if sources:
            serializer = SourceSerializer(sources, many=True)
            return Response(serializer.data,
                    status=HTTP_201_CREATED)
        else:
            return Response(status=HTTP_204_NO_CONTENT)
