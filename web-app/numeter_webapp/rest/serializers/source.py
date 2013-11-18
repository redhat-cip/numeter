"""
Source Serializer module.
"""

from rest_framework import serializers
from core.models import Data_Source as Source


class SourceSerializer(serializers.ModelSerializer):
    """Simple Source Serializer."""
    plugin = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='data_source-detail')
    fullname = serializers.Field(source='__unicode__')

    class Meta:
        model = Source
        fields = ('name', 'plugin', 'comment', 'url', 'id', 'fullname')
