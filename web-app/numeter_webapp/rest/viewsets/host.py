"""
Host ViewSet module.
"""

from rest_framework import viewsets
from core.models import Host
from rest.permissions import IsOwnerOrForbidden


class HostViewSet(viewsets.ModelViewSet):
    """
    Host endpoint, availaible for all users. It filters Hosts by user
    and only display data for host in same the group of user.
    """
    model = Host
    permission_classes = (IsOwnerOrForbidden,)

    def get_queryset(self):
        return self.model.objects.user_filter(self.request.user)
