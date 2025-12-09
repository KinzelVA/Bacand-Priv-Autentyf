# mock_business/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from access_control.permissions import AccessRequiredPermission
from access_control.utils import get_rule_for

MOCK_ORDERS = [
    {"id": 1, "owner_id": 1, "title": "Заказ 1 пользователя 1"},
    {"id": 2, "owner_id": 2, "title": "Заказ 2 пользователя 2"},
    {"id": 3, "owner_id": 1, "title": "Заказ 3 пользователя 1"},
]


class OrdersListView(APIView):
    """
    Бизнес-объект "orders".

    Доступ:
      - 401, если не аутентифицирован (обрабатывает DRF + JWTAuthentication)
      - 403, если прав на чтение нет (AccessRequiredPermission)
      - если есть read_all_permission — видит все заказы
      - если только read_permission — видит только свои
    """
    permission_classes = [IsAuthenticated, AccessRequiredPermission]
    element_code = "orders"

    def get(self, request):
        rule = get_rule_for(request.user, self.element_code)

        if rule and rule.read_all_permission:
            data = MOCK_ORDERS
        else:
            user_id = request.user.id
            data = [o for o in MOCK_ORDERS if o["owner_id"] == user_id]

        return Response(data)

