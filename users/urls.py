from django.urls import path, include
from .api import UserViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
