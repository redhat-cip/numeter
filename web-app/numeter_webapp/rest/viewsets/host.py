"""
Host ViewSet file.
"""

from rest_framework import viewsets
from core.models import Host
from rest.permissions import IsOwnerOrForbidden


class HostViewSet(viewsets.ModelViewSet):
    model = Host
    permission_classes = (IsOwnerOrForbidden,)

    def get_queryset(self):
        return self.model.objects.user_filter(self.request.user)
