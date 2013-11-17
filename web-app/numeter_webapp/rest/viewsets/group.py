"""
Group ViewSet module.
"""

from rest_framework import viewsets
from core.models import Group


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group endpoint, only available for superusers.
    """
    model = Group
