"""
User ViewSet file.
"""

from rest_framework import viewsets
from core.models import User


class UserViewSet(viewsets.ModelViewSet):
    model = User
