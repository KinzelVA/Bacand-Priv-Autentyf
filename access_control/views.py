# access_control/views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccessRoleRule, BusinessElement, Role
from .permissions import IsAdminRolePermission
from .serializers import (
    AccessRoleRuleSerializer,
    BusinessElementSerializer,
    RoleSerializer,
)


class RoleListCreateView(APIView):
    """
    GET /api/access/roles/   — список ролей
    POST /api/access/roles/  — создание роли

    Только для admin.
    """

    permission_classes = [IsAuthenticated, IsAdminRolePermission]

    def get(self, request):
        roles = Role.objects.all().order_by("id")
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class BusinessElementListCreateView(APIView):
    """
    GET /api/access/elements/   — список бизнес-элементов
    POST /api/access/elements/  — создание элемента

    Только для admin.
    """

    permission_classes = [IsAuthenticated, IsAdminRolePermission]

    def get(self, request):
        elements = BusinessElement.objects.all().order_by("id")
        serializer = BusinessElementSerializer(elements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BusinessElementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        element = serializer.save()
        return Response(
            BusinessElementSerializer(element).data,
            status=status.HTTP_201_CREATED,
        )


class AccessRoleRuleListCreateView(APIView):
    """
    GET /api/access/rules/    — список правил доступа
    POST /api/access/rules/   — создание правила

    Только для admin.
    """

    permission_classes = [IsAuthenticated, IsAdminRolePermission]

    def get(self, request):
        rules = AccessRoleRule.objects.select_related("role", "element").all()
        serializer = AccessRoleRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccessRoleRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule = serializer.save()
        return Response(
            AccessRoleRuleSerializer(rule).data,
            status=status.HTTP_201_CREATED,
        )


class AccessRoleRuleDetailView(APIView):
    """
    PATCH /api/access/rules/<id>/   — частичное обновление правила
    DELETE /api/access/rules/<id>/  — удаление правила

    Только для admin.
    """

    permission_classes = [IsAuthenticated, IsAdminRolePermission]

    def get_object(self, pk):
        return AccessRoleRule.objects.select_related("role", "element").get(pk=pk)

    def patch(self, request, pk):
        rule = self.get_object(pk)
        serializer = AccessRoleRuleSerializer(
            rule,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        rule = serializer.save()
        return Response(AccessRoleRuleSerializer(rule).data)

    def delete(self, request, pk):
        rule = self.get_object(pk)
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

