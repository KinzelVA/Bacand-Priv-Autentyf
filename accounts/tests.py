# accounts/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthFlowTests(APITestCase):
    """
    Проверяет, что:
    - пользователь может зарегистрироваться;
    - затем залогиниться по email+пароль;
    - затем получить свои данные по /api/auth/me/.
    """

    def test_register_login_me_flow(self):
        register_url = reverse("auth-register")
        login_url = reverse("auth-login")
        me_url = reverse("auth-me")

        # 1) Регистрация
        register_data = {
            "email": "user1@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
        }
        response = self.client.post(register_url, register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], register_data["email"])

        # Проверяем, что пользователь действительно создан в БД
        self.assertTrue(User.objects.filter(email=register_data["email"]).exists())

        # 2) Логин
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"],
        }
        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        access_token = response.data["access"]

        # 3) /me с токеном
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], register_data["email"])
        self.assertEqual(response.data["first_name"], register_data["first_name"])
        self.assertEqual(response.data["last_name"], register_data["last_name"])

