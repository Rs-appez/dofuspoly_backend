from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib import admin
from django.urls import path, include

from monopoly.urls import websocket_urlpatterns as monopoly_websocket_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("dofuspoly/", include("monopoly.urls")),
]

websocket_urlpatterns = monopoly_websocket_urlpatterns
