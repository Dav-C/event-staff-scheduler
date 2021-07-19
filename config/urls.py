from django.contrib import admin
from django.urls import path, include
import ess_app.urls

urlpatterns = [
    path("admin", admin.site.urls),
    path("", include(ess_app.urls)),
]
