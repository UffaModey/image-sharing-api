from django.urls import path, include
from .api import (
    PostViewSet,
    FollowViewSet,
    MutualFollowViewSet,
    FollowSuggestionsViewSet,
    PostLikeView,
    PostUnlikeView
                  )
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    path('post/<uuid:post_id>/like', PostLikeView.as_view({'post': 'create', 'get': 'list'}), name='post-like'),
    path('post/<uuid:post_id>/unlike', PostUnlikeView.as_view({'delete': 'destroy'}), name='post-unlike'),
    path('mutual-follow/<uuid:pk>/', MutualFollowViewSet.as_view({'get': 'list'}), name='mutual-following'),
    path('follow-suggestions/', FollowSuggestionsViewSet.as_view({'get': 'list'}), name='follow-suggestions')
]
