"""
Storage ViewSet module.
"""

from rest_framework import viewsets
from core.models import Storage


class StorageViewSet(viewsets.ModelViewSet):
    """
    User endpoint, only available for superusers.
    """
    model = Storage
