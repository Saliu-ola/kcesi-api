from rest_framework.permissions import BasePermission, SAFE_METHODS

ADMIN_ROLE_ID = 2
SUPER_ADMIN_ROLE_ID = 1
USER_ROLE_ID = 3


class IsAdmin(BasePermission):
    """Allows access only to admin users."""

    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == ADMIN_ROLE_ID)


class IsSuperAdmin(BasePermission):
    """Allows access only to superadmin users."""

    message = "Only SuperAdmin are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == SUPER_ADMIN_ROLE_ID)


class IsUser(BasePermission):
    """Allows access only to  users."""

    message = "Only Users are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role_id == USER_ROLE_ID)


class IsSuperOrAdminAdmin(BasePermission):

    """Allows access only to  super_admin users."""

    message = "Only SuperAdmins or Regular Admin are authorized to perform this action."

    def has_permission(self, request, view):
        """There is a need to use admin for backward compatibility on Mobile app"""
        return bool(
            request.user.is_authenticated and request.user.role_id == SUPER_ADMIN_ROLE_ID
        ) or bool(request.user.is_authenticated and request.user.role_id == ADMIN_ROLE_ID)
