"""
Skeleton ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet
from multiviews.models import Skeleton
from rest.serializers import SkeletonSerializer
from rest.permissions import IsOwnerOrForbidden
from rest.views import ModelListDelete


class SkeletonViewSet(ModelListDelete, ModelViewSet):
    """
    Skeleton endpoint, availaible for all users. It filters by its view's 
    user and groups.
    """
    model = Skeleton
    permission_classes = (IsOwnerOrForbidden,)
    serializer_class = SkeletonSerializer
    allowed_methods = ('POST', 'PATCH', 'DELETE', 'GET')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)
