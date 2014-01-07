"""
Source ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet 
from core.models import Data_Source as Source
from rest.permissions import IsOwnerOrForbidden
from rest.serializers import SourceSerializer
from rest.views import ModelListDelete


class SourceViewSet(ModelListDelete, ModelViewSet):
    """
    Source endpoint, availaible for all users. It filters Sources by user
    and only display data for source in same the group of user.
    """
    model = Source
    permission_classes = (IsOwnerOrForbidden,)
    allowed_methods = ('GET', 'PATCH', 'DELETE')
    serializer_class = SourceSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        objects = self.model.objects.user_web_filter(q, self.request.user)
        # ID filter
        ids = self.request.QUERY_PARAMS.get('id', [])
        try:
            objects = objects.filter(id__in=ids) if ids else objects
        except ValueError:
            from json import loads
            ids = loads(ids)
            objects = objects.filter(id__in=ids) if ids else objects
        return objects
