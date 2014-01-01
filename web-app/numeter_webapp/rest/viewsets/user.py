"""
User ViewSet module.
"""

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import User
from rest.serializers import UserSerializer, PasswordSerializer
from rest.permissions import IsSelfOrForbidden, IsOwnerOrForbidden, HostPermission
from rest.views import ModelListDelete


class UserViewSet(ModelListDelete, viewsets.ModelViewSet):
    """
    User endpoint, only available for superusers, except details for user himself.
    Contains a ``set_password`` method for manage password.
    """
    model = User
    permission_classes = (IsOwnerOrForbidden, HostPermission)
    serializer_class = UserSerializer
    allowed_methods = ('GET', 'PATCH', 'DELETE', 'POST')

    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        if self.request.method != 'GET':
            return self.model.objects.user_web_filter(q, self.request.user)
        return self.model.objects.user_web_filter(q, self.request.user).filter(is_superuser=False)

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


class SuperuserViewSet(UserViewSet):
    """User endpoint, only available for superusers."""
    def get_queryset(self):
        q = self.request.QUERY_PARAMS.get('q', '')
        if self.request.method != 'GET':
            return self.model.objects.user_web_filter(q, self.request.user)
        return self.model.objects.user_web_filter(q, self.request.user).filter(is_superuser=True)
