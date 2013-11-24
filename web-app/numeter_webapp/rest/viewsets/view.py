"""
View ViewSet module.
"""

from rest_framework.viewsets import ModelViewSet 
from multiviews.models import View
from rest.serializers import ViewSerializer
from rest.permissions import IsOwnerOrForbidden
from rest.views import ModelListDelete


class ViewViewSet(ModelListDelete, ModelViewSet):
    """
    View endpoint, availaible for all users. It filters View by its user and
    groups.
    """
    model = View
    permission_classes = (IsOwnerOrForbidden,)
    serializer_class = ViewSerializer
    allowed_methods = ('POST', 'PATCH', 'DELETE', 'GET')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)
