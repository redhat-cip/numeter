"""
Multiview ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet
from multiviews.models import Multiview
from rest.serializers import MultiviewSerializer
from rest.permissions import IsOwnerOrForbidden
from rest.views import ModelListDelete


class MultiviewViewSet(ModelListDelete, ModelViewSet):
    """
    Multiview endpoint, availaible for all users. It filters by its view's 
    user and groups.
    """
    model = Multiview
    permission_classes = (IsOwnerOrForbidden,)
    serializer_class = MultiviewSerializer
    allowed_methods = ('POST', 'PATCH', 'DELETE', 'GET')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        objects = self.model.objects.user_web_filter(q, self.request.user)
        # ID filter
        ids = self.request.QUERY_PARAMS.get('id', [])
        objects = objects.filter(id__in=ids) if ids else objects
        return objects
