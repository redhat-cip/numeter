"""
Group ViewSet module.
"""

from rest_framework import viewsets
from core.models import Group
from rest.serializers import GroupSerializer
from rest.views import ModelListDelete


class GroupViewSet(ModelListDelete, viewsets.ModelViewSet):
    """
    Group endpoint, only available for superusers.
    """
    model = Group
    serializer_class = GroupSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        objects = self.model.objects.web_filter(q)
        # ID filter
        ids = self.request.QUERY_PARAMS.get('id', [])
        # TODO: Clarify why could be not JSON ??
        try:
            objects = objects.filter(id__in=ids) if ids else objects
        except ValueError:
            from json import loads
            print ids
            ids = loads(ids)
            objects = objects.filter(id__in=ids) if ids else objects
        return objects
