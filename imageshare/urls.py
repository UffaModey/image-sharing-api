from django.urls import path, include
from .api import PostViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register(r'', PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
]
