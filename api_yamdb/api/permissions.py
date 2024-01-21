from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права доступа: администратор, суперпользователь или только
    чтение для SAFE_METHODS."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin()
        )


class IsAuthorAdminSuperuserOrReadOnlyPermission(permissions.BasePermission):
    """Права доступа: автор объекта, администратор, суперпользователь или
    только чтение для SAFE_METHODS."""

    def has_permission(self, request, view):
        """Определяет права на уровне запроса и пользователя."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Определяет права на уровне объекта."""
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_admin()
                    or request.user.is_moderator()
                    or obj.author == request.user))


class IsAdminPermission(permissions.BasePermission):
    """Права доступа: администратор или суперпользователь."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()
