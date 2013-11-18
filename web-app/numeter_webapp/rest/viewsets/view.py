"""
View ViewSet module.
"""

from rest_framework import viewsets
from multiviews.models import View
from rest.serializers import ViewSerializer
from rest.permissions import IsOwnerOrForbidden


class ViewViewSet(viewsets.ModelViewSet):
    """
    View endpoint, availaible for all users. It filters View by its user and
    groups.
    """
    model = View
    permission_classes = (IsOwnerOrForbidden,)
    serializer_class = ViewSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)
