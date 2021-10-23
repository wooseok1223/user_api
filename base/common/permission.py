from rest_framework.permissions import BasePermission


def _is_user_authenticated(request):
    return request.user and request.user.is_authenticated


def user_permission(request):
    if request.method not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        return False

    try:
        return True
    except request.user.ObjectDoesNotExist:
        return False


class UserCheck(BasePermission):

    def has_permission(self, request, view):
        if not _is_user_authenticated(request):
            return False

        return user_permission(request) or False
