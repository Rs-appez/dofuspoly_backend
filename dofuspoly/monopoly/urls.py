from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"board", views.BoardViewSet)
router.register(r"game", views.GameViewSet)
router.register(r"player", views.PlayerViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
