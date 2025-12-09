# accounts/authentication.py
import jwt
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import AuthToken
from .utils import decode_jwt

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Аутентификация по заголовку:
    Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            # Нет заголовка — пусть DRF попробует другие схемы (или вернёт 401)
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed("Неверный формат заголовка Authorization")

        raw_token = parts[1]

        try:
            payload = decode_jwt(raw_token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Срок действия токена истёк")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Невалидный токен")

        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise AuthenticationFailed("Некорректный payload токена")

        try:
            token_obj = AuthToken.objects.select_related("user").get(jti=jti)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed("Токен не найден или отозван")

        if token_obj.is_revoked:
            raise AuthenticationFailed("Токен отозван")

        if token_obj.is_expired:
            raise AuthenticationFailed("Срок действия токена истёк")

        user = token_obj.user

        if not user.is_active:
            raise AuthenticationFailed("Пользователь деактивирован")

        return user, token_obj
