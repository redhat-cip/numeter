"""
Group Serializer module.
"""

from rest_framework import serializers
from core.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """Simple Group Serializer."""
    url = serializers.HyperlinkedIdentityField(view_name='group-detail')
    text = serializers.Field(source='__unicode__')

    class Meta:
        model = Group
        fields = ('name', 'url', 'id', 'text',)
