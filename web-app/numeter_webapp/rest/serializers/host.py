"""
Host Serializer module.
"""

from rest_framework import serializers
from core.models import Storage, Host


class HostSerializer(serializers.ModelSerializer):
    """Simple host serializer."""
    storage = serializers.PrimaryKeyRelatedField()
    group = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='host-detail')
    class Meta:
        model = Host
        fields = ('id', 'name', 'hostid', 'group', 'storage', 'url')


class HostUserSerializer(serializers.ModelSerializer):
    """Simple host serializer."""
    class Meta:
        model = Host
        fields = ('name', 'hostid',)


class HostCreationSerializer(serializers.ModelSerializer):
    """Host creation serializer. Use only hostid to create instance."""
    class Meta:
        model = Host
        fields = ('hostid',)

    def validate_hostid(self, attrs, source):
        value = attrs[source]
        self.storage = Storage.objects.which_storage(value)
        if not self.storage:
            raise serializers.ValidationError('No host with this ID found.')
        return attrs

    def save(self):
        return self.storage.create_host(self.init_data['hostid'])
