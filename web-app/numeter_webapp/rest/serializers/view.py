"""
View Serializer module.
"""

from rest_framework import serializers
from multiviews.models import View


class ViewSerializer(serializers.ModelSerializer):
    """Simple View Serializer."""
    users = serializers.PrimaryKeyRelatedField(many=True)
    groups = serializers.PrimaryKeyRelatedField(many=True)
    sources = serializers.PrimaryKeyRelatedField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='view-detail')
    fullname = serializers.Field(source='__unicode__')

    class Meta:
        model = View
        fields = ('name', 'sources', 'comment', 'warning', 'critical', 'users', 'groups', 'id', 'fullname', 'url')
