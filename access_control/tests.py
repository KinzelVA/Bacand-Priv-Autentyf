# access_control/tests.py
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


User = get_user_model()


class OrdersAccessTests(APITestCase):
    """
    Проверяет:
    - обычный пользователь без правил доступа к 'orders' получает 403;
    - админ с правилом read_all_permission=True получает 200 и список заказов.
    """

    def setUp(self):
        # Роли
        self.role_admin = Role.objects.create(
            name="admin",
            description="Администратор",
        )
        self.role_user = Role.objects.create(
            name="user",
            description="Обычный пользователь",
        )

        # Пользователь-админ
        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin",  # username нужен AbstractUser
            password="adminpass123",
            first_name="Admin",
            last_name="User",
        )
        UserRole.objects.create(user=self.admin, role=self.role_admin)

        # Обычный пользователь
        self.user = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="userpass123",
            first_name="User",
            last_name="Two",
        )
        UserRole.objects.create(user=self.user, role=self.role_user)

        # Бизнес-элемент 'orders'
        self.orders_element = BusinessElement.objects.create(
            code="orders",
            name="Заказы",
        )

        # Правило: админ может читать все заказы
        AccessRoleRule.objects.create(
            role=self.role_admin,
            element=self.orders_element,
            read_permission=True,
            read_all_permission=True,
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
        Вспомогательный метод: залогиниться и получить access-токен.
        """
        response = self.client.post(
            self.login_url,
            {"email": email, "password": password},
            format="json",
        )
        # На случай, если что-то сломается — сразу понятное сообщение
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Login failed for {email}: {response.status_code} {response.data}",
        )
        return response.data["access"]

    def test_orders_forbidden_for_regular_user(self):
        """
        Обычный пользователь без правил на 'orders' должен получать 403.
        """
        token = self.get_token("user2@example.com", "userpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_orders_allowed_for_admin(self):
        """
        Админ с правилом read_all_permission=True должен видеть список заказов (200).
        """
        token = self.get_token("admin@example.com", "adminpass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

