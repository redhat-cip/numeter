"""
Source ViewSet module.
"""

from rest_framework import viewsets
from core.models import Data_Source as Source
from rest.permissions import IsOwnerOrForbidden
from rest.serializers import SourceSerializer


class SourceViewSet(viewsets.ModelViewSet):
    """
    Source endpoint, availaible for all users. It filters Sources by user
    and only display data for source in same the group of user.
    """
    model = Source
    permission_classes = (IsOwnerOrForbidden,)
    allowed_methods = ('GET', 'PATCH', 'DELETE')
    serializer_class = SourceSerializer
    filter_fields = ('name',)

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)
