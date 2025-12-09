# accounts/models.py
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Кастомный пользователь:
    - логин по email
    - добавлено отчество (middle_name)
    """
    middle_name = models.CharField("Отчество", max_length=150, blank=True)
    email = models.EmailField("Email", unique=True)

    # username оставляем, но логинимся по email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # чтобы не ломать админку

    def __str__(self):
        fio = " ".join(filter(None, [self.last_name, self.first_name, self.middle_name]))
        return fio or self.email


class AuthToken(models.Model):
    """
    Таблица для хранения активных JWT-токенов.
    По сути, это "сессия" пользователя.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_tokens",
    )
    jti = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "JWT токен"
        verbose_name_plural = "JWT токены"

    def __str__(self):
        return f"{self.user} | {self.jti} | revoked={self.is_revoked}"

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

