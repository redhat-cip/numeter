"""
Skeleton ViewSet module.
"""

from rest_framework import viewsets
from multiviews.models import Skeleton
from rest.serializers import SkeletonSerializer


class SkeletonViewSet(viewsets.ModelViewSet):
    """
    Skeleton endpoint, availaible for all users. It filters by its view's 
    user and groups.
    """
    model = Skeleton
    serializer_class = SkeletonSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)


