"""
Source ViewSet module.
"""

from rest_framework import viewsets
from core.models import Data_Source as Source
from rest.permissions import IsOwnerOrForbidden


class SourceViewSet(viewsets.ModelViewSet):
    """
    Source endpoint, availaible for all users. It filters Sources by user
    and only display data for source in same the group of user.
    """
    model = Source
    permission_classes = (IsOwnerOrForbidden,)
    allowed_methods = ('GET', 'PATCH', 'DELETE')

    def get_queryset(self):
        return self.model.objects.user_filter(self.request.user)
