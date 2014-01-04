"""
Plugin Serializer module.
"""

from rest_framework import serializers
from core.models import Plugin


class PluginSerializer(serializers.ModelSerializer):
    """Simple Plugin Serializer."""
    host = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='plugin-detail')

    class Meta:
        model = Plugin
        fields = ('name', 'host', 'comment', 'url', 'id')
