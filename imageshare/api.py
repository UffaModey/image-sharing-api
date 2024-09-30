# Third Party Stuff
from rest_framework import status, viewsets, permissions, generics

from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
        List all posts created by the logged-in user or create a new post.
        to do: change this to list all posts by a specified user
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return posts created by the authenticated user
        return Post.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Set the created_by field to the current user when creating a post
        serializer.save(created_by=self.request.user)

    def get_object(self):
        # Get the post and ensure the current user is the owner
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post

    def perform_update(self, serializer):
        # Ensure only the post owner can update the post
        if self.get_object().created_by != self.request.user:
            raise PermissionDenied("You do not have permission to update this post.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure only the post owner can delete the post
        if instance.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()


