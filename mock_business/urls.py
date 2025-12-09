# mock_business/urls.py
from django.urls import path

from .views import OrdersListView

urlpatterns = [
    path("orders/", OrdersListView.as_view(), name="orders-list"),
]
