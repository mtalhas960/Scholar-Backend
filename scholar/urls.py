"""
Scholar.io — URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/scholarships/", include("scholarships.urls")),
    path("api/bookmarks/", include("bookmarks.urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/admin/", include("admin_custom.urls")),
]
