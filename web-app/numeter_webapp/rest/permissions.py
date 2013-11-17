"""
REST API permissions module.
"""

from rest_framework import permissions


class IsOwnerOrForbidden(permissions.IsAuthenticated):
    """
    Permission is granted for superusers or users linked to obj.
    It uses ``model.user_has_perm``.
    """
    def has_permission(self, request, view):
        if not request.user.pk:
            return False
        if request.method in view.allowed_methods:
            return True
        return False

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


class HostPermission(permissions.IsAuthenticated):
    """
    Permission is granted for superusers and the user who has a group same as host.
    POST, DELETE & PATCH are only available for superuser.
    It uses ``Host.user_has_perm``.
    """
    def has_permission(self, request, view):
        if not request.user.pk:
            return False
        if request.method in ('POST', 'DELETE', 'PATCH') and not request.user.is_superuser:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user_has_perm(request.user)
