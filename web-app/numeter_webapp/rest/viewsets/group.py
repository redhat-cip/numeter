"""
Group ViewSet module.
"""

from rest_framework import viewsets
from core.models import Group
from rest.serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group endpoint, only available for superusers.
    """
    model = Group
    serializer_class = GroupSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.web_filter(q)
