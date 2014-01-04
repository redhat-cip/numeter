"""
Skeleton Serializer module.
"""

from rest_framework import serializers
from multiviews.models import Skeleton


class SkeletonSerializer(serializers.ModelSerializer):
    """Simple Skeleton Serializer."""
    url = serializers.HyperlinkedIdentityField(view_name='skeleton-detail')

    class Meta:
        model = Skeleton
        fields = ('name', 'plugin_pattern', 'source_pattern', 'comment', 'url', 'id')
