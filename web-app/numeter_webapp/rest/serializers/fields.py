"""
Custom Serializer Field module.
"""

from rest_framework.serializers import PrimaryKeyRelatedField


class NestedSerializerField(PrimaryKeyRelatedField):
    """Allow to use dictionnary instead of simple id."""
    def from_native(self, value):
        """Return value  or if it's a dict return 'id' value."""
        if isinstance(value, dict):
            return value['id']
        return value
