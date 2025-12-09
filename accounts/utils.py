# accounts/utils.py
from datetime import timedelta
from django.urls import path
import jwt
from django.conf import settings
from django.utils import timezone
from .models import AuthToken


def create_jwt_for_user(user):
    """
    Создаёт запись AuthToken в БД и генерирует JWT.
    """
    lifetime = getattr(settings, "JWT_ACCESS_TOKEN_LIFETIME", timedelta(hours=1))
    expires_at = timezone.now() + lifetime

    token_obj = AuthToken.objects.create(
        user=user,
        expires_at=expires_at,
    )

    payload = {
        "sub": str(user.id),
        "jti": str(token_obj.jti),
        "exp": expires_at,  # PyJWT умеет работать с datetime
    }

    encoded = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # В PyJWT 2.x возвращает str, в 1.x — bytes. Приведём к str на всякий случай.
    if isinstance(encoded, bytes):
        encoded = encoded.decode("utf-8")

    return encoded, token_obj


def decode_jwt(token: str) -> dict:
    """
    Декодирует JWT и возвращает payload.
    Исключения (ExpiredSignatureError, InvalidTokenError) пусть ловит аутентификатор.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

