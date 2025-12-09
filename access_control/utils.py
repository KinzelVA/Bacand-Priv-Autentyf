# access_control/utils.py
from django.core.exceptions import ObjectDoesNotExist

from .models import AccessRoleRule, BusinessElement, UserRole


def get_rule_for(user, element_code: str):
    """
    Возвращает правило доступа для пользователя к бизнес-элементу.
    Если роли/элемента/правила нет — возвращает None.
    """
    if not user or not user.is_authenticated:
        return None

    # вытаскиваем роль пользователя
    try:
        user_role = user.user_role
    except ObjectDoesNotExist:
        return None

    # находим бизнес-элемент по коду
    try:
        element = BusinessElement.objects.get(code=element_code)
    except BusinessElement.DoesNotExist:
        return None

    # ищем правило для пары (роль, элемент)
    try:
        return AccessRoleRule.objects.get(role=user_role.role, element=element)
    except AccessRoleRule.DoesNotExist:
        return None
