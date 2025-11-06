from django.urls import path, include, re_path
from . import views
from .consumers import GameSyncConsumer
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"board", views.BoardViewSet)
router.register(r"game", views.GameViewSet)
router.register(r"player", views.PlayerViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<game_id>\w+)/?$", GameSyncConsumer.as_asgi()),
]
