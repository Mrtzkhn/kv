from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KeyValueViewSet

router = DefaultRouter()
router.register(r"", KeyValueViewSet, basename="keyvalue")

urlpatterns = [
    path("", include(router.urls)),
]
