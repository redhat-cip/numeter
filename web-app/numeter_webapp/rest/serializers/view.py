"""
View Serializer module.
"""

from rest_framework import serializers
from multiviews.models import View
from rest.serializers.fields import NestedSerializerField


class ViewSerializer(serializers.ModelSerializer):
    """Simple View Serializer."""
    users = serializers.PrimaryKeyRelatedField(many=True)
    groups = serializers.PrimaryKeyRelatedField(many=True)
    sources = NestedSerializerField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='view-detail')
    text = serializers.Field(source='__unicode__')

    class Meta:
        model = View
        fields = ('name', 'sources', 'comment', 'warning', 'critical', 'users', 'groups', 'id', 'text', 'url')
