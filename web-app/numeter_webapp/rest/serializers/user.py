"""
User Serializer module.
"""

from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer."""
    class Meta:
        model = User
        fields = ('username', 'email', 'is_superuser', 'groups', 'graph_lib')


class PasswordSerializer(serializers.ModelSerializer):
    """User's password serializer."""
    class Meta:
        model = User
        fields = ('password',)
