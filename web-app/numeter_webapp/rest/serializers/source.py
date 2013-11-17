"""
Source Serializer module.
"""

from rest_framework import serializers
from core.models import Data_Source as Source


class SourceSerializer(serializers.ModelSerializer):
    """Simple Source Serializer."""
    plugin = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='data_source-detail')
    class Meta:
        model = Source
        fields = ('name', 'plugin', 'comment','url')
