from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'board', views.BoardViewSet)
router.register(r'color', views.ColorViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'game', views.GameViewSet)
router.register(r'rent', views.RentViewSet)
router.register(r'case_type', views.CaseTypeViewSet)
router.register(r'card', views.CardViewSet)
router.register(r'card_type', views.CardTypeViewSet)
router.register(r'player', views.PlayerViewSet)


urlpatterns = [
    path('', include(router.urls)),
]