# access_control/permissions.py
# access_control/permissions.py
from rest_framework.permissions import BasePermission

from .utils import get_rule_for


class AccessRequiredPermission(BasePermission):
    """
    Проверяет базовое право на операцию с бизнес-элементом.

    Код элемента берётся из view.element_code (например, "orders").
    """

    def has_permission(self, request, view):
        element_code = getattr(view, "element_code", None)
        if not element_code:
            # Если элемент не задан — не ограничиваем
            return True

        rule = get_rule_for(request.user, element_code)
        if not rule:
            return False

        method = request.method.upper()

        if method == "GET":
            return bool(rule.read_permission or rule.read_all_permission)

        if method == "POST":
            return bool(rule.create_permission)

        if method in ("PUT", "PATCH"):
            return bool(rule.update_permission or rule.update_all_permission)

        if method == "DELETE":
            return bool(rule.delete_permission or rule.delete_all_permission)

        return False


class IsAdminRolePermission(BasePermission):
    """
    Разрешает доступ только пользователю с ролью 'admin'.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_role = getattr(user, "user_role", None)
        if not user_role or not user_role.role:
            return False

        return user_role.role.name == "admin"
