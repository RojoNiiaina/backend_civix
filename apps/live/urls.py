from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LiveStreamViewSet, LiveMessageViewSet, LiveViewerViewSet

router = DefaultRouter()
router.register(r'streams', LiveStreamViewSet)
router.register(r'messages', LiveMessageViewSet)
router.register(r'viewers', LiveViewerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
