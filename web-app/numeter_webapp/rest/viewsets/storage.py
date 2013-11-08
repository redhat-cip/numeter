"""
Storage ViewSet file.
"""

from rest_framework import viewsets
from core.models import Storage


class StorageViewSet(viewsets.ModelViewSet):
    model = Storage
