"""
REST API permissions module.
"""

from rest_framework import permissions


class IsOwnerOrForbidden(permissions.BasePermission):
    """
    Permission is granted for superusers or users linked to obj.
    It uses ``model.user_has_perm``.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user_has_perm(request.user)

class IsSelfOrForbidden(permissions.BasePermission):
    """
    Permission is granted for superusers and the user himself.
    Created to manage users updating.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user
