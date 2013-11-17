"""
Plugin ViewSet module.
"""

from rest_framework import viewsets
from core.models import Plugin
from rest.permissions import IsOwnerOrForbidden


class PluginViewSet(viewsets.ModelViewSet):
    """
    Plugin endpoint, availaible for all users. It filters Plugins by user
    and only display data for plugin in same the group of user.
    """
    model = Plugin
    permission_classes = (IsOwnerOrForbidden,)
    allowed_methods = ('GET', 'PATCH', 'DELETE')

    def get_queryset(self):
        return self.model.objects.user_filter(self.request.user)
