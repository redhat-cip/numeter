"""
Multiview Serializer module.
"""

from rest_framework import serializers
from multiviews.models import Multiview


class MultiviewSerializer(serializers.ModelSerializer):
    """Simple View Serializer."""
    views = serializers.PrimaryKeyRelatedField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='multiview-detail')
    class Meta:
        model = Multiview
        fields = ('name', 'views', 'comment', 'id',)

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        return self.model.objects.user_web_filter(q, self.request.user)

