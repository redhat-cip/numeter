"""
Multiview Serializer module.
"""

from rest_framework import serializers
from multiviews.models import Multiview
from rest.serializers.fields import NestedSerializerField


class MultiviewSerializer(serializers.ModelSerializer):
    """Simple View Serializer."""
    views = NestedSerializerField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='multiview-detail')
    text = serializers.Field(source='__unicode__')

    class Meta:
        model = Multiview
        fields = ('name', 'views', 'comment', 'id', 'url', 'text')
