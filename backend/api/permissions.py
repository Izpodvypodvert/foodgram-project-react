from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.models import ADMIN, BANNED


class IsUserNotBanned(BasePermission):
    """Проверяет забанен ли пользователь."""

    def has_permission(self, request, view):
        try:
            return bool(request.user.is_anonymous
                        or request.user.role != BANNED)
        except AttributeError:
            return False


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на изменение только для админов.
    Остальным пользователям только чтение объекта."""

    def has_permission(self, request, view):
        try:
            return bool(request.method in SAFE_METHODS
                        or request.user.role == ADMIN)
        except AttributeError:
            return False


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Разрешение на изменение только для админов и автора.
    Остальным пользователям только чтение объекта."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        try:
            return bool(request.method in SAFE_METHODS
                        or request.user == obj.author
                        or request.user.role == ADMIN)
        except AttributeError:
            return False
