# accounts/views.py
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthToken
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
    UserSerializer,
)
from .utils import create_jwt_for_user


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Регистрация нового пользователя.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Логин по email + пароль. Возвращает access-токен.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        access_token, token_obj = create_jwt_for_user(user)

        return Response(
            {
                "access": access_token,
                "token_type": "Bearer",
                "expires_at": token_obj.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Отзывает текущий токен.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_obj = request.auth
        if isinstance(token_obj, AuthToken):
            token_obj.is_revoked = True
            token_obj.save(update_fields=["is_revoked"])
        return Response({"detail": "Вы вышли из системы"}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    GET /api/auth/me/      — получить свои данные
    PATCH /api/auth/me/    — обновить свои данные
    DELETE /api/auth/me/   — мягкое удаление (is_active=False)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UpdateUserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])

        # Отзываем все активные токены
        AuthToken.objects.filter(user=user, is_revoked=False).update(is_revoked=True)

        return Response(
            {"detail": "Пользователь деактивирован"},
            status=status.HTTP_200_OK,
        )

