# em_auth/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("mock_business.urls")),
    path("api/auth/", include("accounts.urls")),
path("api/access/", include("access_control.urls")),
]

