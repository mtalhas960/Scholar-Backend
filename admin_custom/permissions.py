from rest_framework.permissions import BasePermission


class IsProjectAdmin(BasePermission):
    """Allow users marked as project admins or Django staff users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_staff)
        )