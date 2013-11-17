"""
Source Serializer module.
"""

from rest_framework import serializers
from core.models import Data_Source as Source


class SourceSerializer(serializers.ModelSerializer):
    """Simple Source Serializer."""
    class Meta:
        model = Source
