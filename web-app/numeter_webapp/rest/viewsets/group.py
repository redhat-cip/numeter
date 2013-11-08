"""
User ViewSet file.
"""

from rest_framework import viewsets
from core.models import Group


class GroupViewSet(viewsets.ModelViewSet):
    model = Group

