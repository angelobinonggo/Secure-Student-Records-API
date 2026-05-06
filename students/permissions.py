"""
permissions.py — Custom RBAC permission classes (Part D of Lab Activity 1)
"""
from rest_framework.permissions import BasePermission


def _in_group(user, *group_names):
    """Helper: True if the authenticated user belongs to any of the named groups."""
    return user.is_authenticated and (
        user.groups.filter(name__in=group_names).exists() or user.is_superuser
    )


class IsAdminUser(BasePermission):
    """
    Grants access only to users in the 'Admin' group (or Django superusers).
    Used for: CREATE and DELETE operations on student records.
    """
    message = "Access denied: Admin role required."

    def has_permission(self, request, view):
        return _in_group(request.user, 'Admin')


class IsAdminOrFaculty(BasePermission):
    """
    Grants access to 'Admin' or 'Faculty' group members.
    Used for: UPDATE operations on student records.
    """
    message = "Access denied: Admin or Faculty role required."

    def has_permission(self, request, view):
        return _in_group(request.user, 'Admin', 'Faculty')


class IsOwnerOrAdminOrFaculty(BasePermission):
    """
    Object-level permission:
    - Admins and Faculty can access any record.
    - Students can ONLY access their own record (owner == request.user).
    """
    message = "Access denied: you can only view your own record."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin / Faculty / Superuser → full access
        if _in_group(request.user, 'Admin', 'Faculty'):
            return True
        # Student → own record only
        return obj.owner == request.user
