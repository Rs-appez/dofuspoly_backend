from django.urls import re_path

from .consumers import GameSyncConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/game/(?P<game_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/?$",
        GameSyncConsumer.as_asgi(),
    ),
]
