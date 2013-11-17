"""
User ViewSet module.
"""

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import User
from rest.serializers import UserSerializer, PasswordSerializer
from rest.permissions import IsSelfOrForbidden


class UserViewSet(viewsets.ModelViewSet):
    """
    User endpoint, only available for superusers, except details for user himself.
    Contains a ``set_password`` method for manage password.
    """
    model = User
    serializer_class = UserSerializer

    @action(permission_classes=[IsSelfOrForbidden])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.DATA)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
