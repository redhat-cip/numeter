"""
User ViewSet module.
"""

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
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
        objects = self.model.objects.user_web_filter(q, self.request.user)
        # ID filter
        ids = self.request.QUERY_PARAMS.get('id', [])
        objects = objects.filter(id__in=ids) if ids else objects
        # Change can be made on super and simple users
        if self.request.method != 'GET':
            return objects
        return objects.filter(is_superuser=False)

    def create(self, request, *args, **kwargs):
        """
        Custom create method. It uses ``UserSerializer`` and ``PasswordSerializer``
        to valid request.
        """
        user_serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if user_serializer.is_valid():
            pass_serializer = PasswordSerializer(data=request.DATA)
            # Only create if fields and password are valid
            if pass_serializer.is_valid():
                self.pre_save(user_serializer.object)
                self.object = user_serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                headers = self.get_success_headers(user_serializer.data)
                # Set password
                self.object.set_password(pass_serializer.data['password'])
                self.object.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED,
                                 headers=headers)
            # Compute user and password serializer errors
            else:
                user_serializer.errors.update(pass_serializer.errors)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @detail_route(permission_classes=[IsSelfOrForbidden])
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
