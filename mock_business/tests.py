# mock_business/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from access_control.models import (
    AccessRoleRule,
    BusinessElement,
    Role,
    UserRole,
)
from mock_business.views import MOCK_ORDERS


User = get_user_model()


class OrdersViewTests(APITestCase):
    """
    Тесты для /api/orders/:
    - без аутентификации возвращает 401;
    - с правилом read_permission=True и read_all_permission=False
      пользователь видит только свои заказы.
    """

    def setUp(self):
        # Роль обычного пользователя
        self.role_user = Role.objects.create(
            name="user",
            description="Обычный пользователь",
        )

        # Создаём пользователя (он, скорее всего, получит id=1)
        self.user = User.objects.create_user(
            email="user_orders@example.com",
            username="user_orders",
            password="userpass123",
            first_name="User",
            last_name="Orders",
        )
        UserRole.objects.create(user=self.user, role=self.role_user)

        # Бизнес-элемент 'orders'
        self.orders_element = BusinessElement.objects.create(
            code="orders",
            name="Заказы",
        )

        # Правило: пользователь может читать ТОЛЬКО свои заказы
        AccessRoleRule.objects.create(
            role=self.role_user,
            element=self.orders_element,
            read_permission=True,
            read_all_permission=False,
            create_permission=False,
            update_permission=False,
            update_all_permission=False,
            delete_permission=False,
            delete_all_permission=False,
        )

        self.login_url = reverse("auth-login")
        self.orders_url = reverse("orders-list")

    def get_token(self, email: str, password: str) -> str:
        """
        Логинимся и возвращаем access-токен.
        """
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Login failed for {email}: {response.status_code} {response.data}",
        )
        return response.data["access"]

    def test_orders_requires_authentication(self):
        """
        Без токена /api/orders/ должен требовать аутентификацию.
        """
        response = self.client.get(self.orders_url)
        # DRF обычно отдаёт 401 с detail про креды
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.assertIn("detail", response.data)

    def test_orders_returns_only_own_orders_when_only_read_permission(self):
        """
        При read_permission=True и read_all_permission=False
        пользователь видит только свои заказы
        """
