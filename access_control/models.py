# access_control/models.py
from django.conf import settings
from django.db import models


class Role(models.Model):
    """
    Роль пользователя (admin, manager, user и т.п.)
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Связь пользователя и роли (по ТЗ достаточно одной роли на пользователя).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_role",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="users",
    )

    class Meta:
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"

    def __str__(self):
        return f"{self.user} -> {self.role}"


class BusinessElement(models.Model):
    """
    Бизнес-объект (users, orders, rules и т.д.)
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Уникальный код элемента (например, 'users', 'orders', 'rules')",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Бизнес-элемент"
        verbose_name_plural = "Бизнес-элементы"

    def __str__(self):
        return self.code


class AccessRoleRule(models.Model):
    """
    Правило доступа:
    - для роли
    - к конкретному бизнес-элементу
    - набор флагов разрешений
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name="rules",
    )

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)

    create_permission = models.BooleanField(default=False)

    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)

    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "element")
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"

    def __str__(self):
        return f"{self.role} -> {self.element}"

