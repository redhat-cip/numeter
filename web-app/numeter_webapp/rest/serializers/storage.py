"""
Storage Serializer module.
"""

from rest_framework import serializers
from core.models import Storage


class StorageSerializer(serializers.ModelSerializer):
    """Simple user serializer."""
    url = serializers.HyperlinkedIdentityField(view_name='storage-detail')
    class Meta:
        model = Storage
        fields = ('name', 'address', 'port', 'url_prefix', 'protocol', 'login', 'password', 'id', 'url')
