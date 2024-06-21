from rest_framework import permissions

ADMIN_ROLE_ID = 2
SUPER_ADMIN_ROLE_ID = 1
USER_ROLE_ID = 3


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == ADMIN_ROLE_ID)


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to superadmin users."""

    message = "Only SuperAdmin are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == SUPER_ADMIN_ROLE_ID)


class IsUser(permissions.BasePermission):
    """Allows access only to  users."""

    message = "Only Users are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == USER_ROLE_ID)


class IsSuperAdminOrAdmin(permissions.BasePermission):

    """Allows access only to  super_admin users."""

    message = "Only SuperAdmins and Regular Admin are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role_id == SUPER_ADMIN_ROLE_ID
        ) or bool(request.user.is_authenticated and request.user.role_id == ADMIN_ROLE_ID)


class IsAdminOrUser(permissions.BasePermission):

    """Allows access only to  super_admin users."""

    message = "Only Admins and  Regular User are authorized to perform this action."

    def has_permission(self, request, view):
        """There is a need to use admin for backward compatibility on Mobile app"""
        return bool(
            request.user.is_authenticated and request.user.role_id == USER_ROLE_ID
        ) or bool(request.user.is_authenticated and request.user.role_id == ADMIN_ROLE_ID)
