"""
Group Serializer module.
"""

from rest_framework import serializers
from core.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """Simple Source Serializer."""
    url = serializers.HyperlinkedIdentityField(view_name='group-detail')
    class Meta:
        model = Group
        fields = ('name', 'url')
