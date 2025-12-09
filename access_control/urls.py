# access_control/urls.py
from django.urls import path

from .views import (
    AccessRoleRuleDetailView,
    AccessRoleRuleListCreateView,
    BusinessElementListCreateView,
    RoleListCreateView,
)

urlpatterns = [
    path("roles/", RoleListCreateView.as_view(), name="roles-list-create"),
    path(
        "elements/",
        BusinessElementListCreateView.as_view(),
        name="elements-list-create",
    ),
    path("rules/", AccessRoleRuleListCreateView.as_view(), name="rules-list-create"),
    path(
        "rules/<int:pk>/",
        AccessRoleRuleDetailView.as_view(),
        name="rules-detail",
    ),
]
