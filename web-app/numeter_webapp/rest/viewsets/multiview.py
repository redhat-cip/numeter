"""
Multiview ViewSet module.
"""

from rest_framework import viewsets
from multiviews.models import Multiview
from rest.serializers import MultiviewSerializer


class MultiviewViewSet(viewsets.ModelViewSet):
    """
    Multiview endpoint, availaible for all users. It filters by its view's 
    user and groups.
    """
    model = Multiview
    serializer_class = MultiviewSerializer

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)

