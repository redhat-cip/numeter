"""
User Serializer module.
"""

from rest_framework import serializers
from core.models import User
from rest.serializers.fields import NestedSerializerField


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer."""
    groups = NestedSerializerField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')
    class Meta:
        model = User
        fields = ('username', 'email', 'is_superuser', 'groups', 'graph_lib', 'url', 'id')


class PasswordSerializer(serializers.ModelSerializer):
    """User's password serializer."""
    class Meta:
        model = User
        fields = ('password',)
