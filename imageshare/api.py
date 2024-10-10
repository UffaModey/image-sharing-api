# Third Party Stuff
from rest_framework import status, viewsets, permissions, generics

from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework import filters
from django.db.models import Q
from .utils.pagination import PostsPagination

from .models import Post, Follow, Like
from users.models import User
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from .serializers import PostSerializer, FollowSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
        List only posts by the authenticated user and their followed users
        (sort by most recent and the number of likes)
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostsPagination
    filter_backends = [filters.SearchFilter]  # Add search filter backend
    search_fields = ['caption']  # Specify fields for search

    def get_queryset(self):
        # Return posts by all users sorted by the number of post likes
        queryset = Post.objects.prefetch_related('likes').all()\
            .annotate(likes_count=Count('likes')).order_by('-likes_count')
        return queryset

    def perform_create(self, serializer):
        # Set the created_by field to the current user when creating a post
        serializer.save(created_by=self.request.user)

    def get_object(self):
        # Get the post and ensure the current user is the owner
        post = get_object_or_404(Post, id=self.kwargs.get('pk'))
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

    @action(methods=["GET"], detail=False)
    def followed(self, request):
        search_query = request.query_params.get('search', None)

        # Retrieve the following users' posts in a single query
        followings_list = list(Follow.objects.filter(created_by=self.request.user).values_list('following', flat=True))
        followings_list.append(self.request.user.id)  # Add the current user to the list

        queryset = self.get_queryset().filter(created_by__in=followings_list).order_by('-created_at')

        # Apply search filter if a search query is provided
        if search_query:
            queryset = queryset.filter(caption__icontains=search_query)

        # Optimize by prefetching and selecting related fields
        queryset = queryset.select_related('created_by').prefetch_related('likes')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, pagination_class=None)
    def publish(self, request):
        post_id = self.request.query_params.get("post_id")
        post = get_object_or_404(Post, id=post_id)

        if post.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")

        data = {
            "shareable_link": str(post.sharable_link)
        }
        return Response(data)


class PostLikeView(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
            Like a post
        """
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))

        # Check if the user already liked the post
        like, created = Like.objects.get_or_create(
            post=post,
            liked_by=self.request.user
        )
        if created:
            return Response({'message': 'Post liked successfully'}, status=201)
        else:
            raise ParseError('You already like this post')

    def list(self, request, *args, **kwargs):
        """
            List all users who liked a post
        """
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        likes = Like.objects.filter(post=post)

        # Prepare data for response
        liked_by_users = [like.liked_by.username for like in likes]
        data = {
            "post_id": post.id,
            "total_likes": likes.count(),
            "liked_by": liked_by_users,
        }

        return Response(data)


class PostUnlikeView(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        like = Like.objects.filter(post=post, liked_by=self.request.user).first()
        if not like:
            raise PermissionDenied("You do not have permission to unlike this post.")
        like.delete()
        return Response({'message': 'Post unliked successfully'}, status=204)


class FollowViewSet(viewsets.ModelViewSet):
    """
        Follow or unfollow a user
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'delete']  # Allow only POST and DELETE methods

    def get_queryset(self):
        # Return follow details for a given user
        return Follow.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Get the user the authenticated user wants to follow using the following_id
        following_id = self.request.data.get("following")
        following = User.objects.get(id=following_id)
        if str(self.request.user.id) == str(following_id):
            raise ParseError('You cannot follow yourself')

        try:
            # Save the follow relationship with the authenticated user as 'created_by'
            serializer.save(created_by=self.request.user, following=following)
        except Exception as e:
            raise ParseError('Unable to follow this user: {}'.format(e))

    def perform_destroy(self, instance):
        # Ensure only the user that created the follow can unfollow
        if instance.created_by != self.request.user:
            raise PermissionDenied("Unable to unfollow user")
        instance.delete()


class MutualFollowersViewSet(viewsets.ViewSet):
    """
    View to show mutual followings between the authenticated user and a target user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')  # Get user_id from URL
        user = get_object_or_404(User, id=user_id)

        # Get the list of users who follow the authenticated user
        self_followers = Follow.objects.filter(following=self.request.user).values_list('created_by__username',
                                                                                        flat=True)
        # Get the list of users who follow the target user
        user_follower = Follow.objects.filter(following=user).values_list('created_by__username', flat=True)

        # Use intersection (&) to find mutuals
        mutuals = set(self_followers) & set(user_follower)

        # Prepare data for response
        data = {
            "mutual_followers": list(mutuals),  # List of mutual following usernames
        }

        return Response(data)


class FollowSuggestionsViewSet(viewsets.ViewSet):
    """
        View to show suggested users for the authenticated user to follow.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # TO DO: improve algorithm later
        suggestions = []

        user = self.request.user
        user_followings = Follow.objects.filter(created_by=user)
        user_followers = Follow.objects.filter(following=user)

        user_followings_users_list = []
        if user_followings:
            for follow in user_followings:
                user_followings_users_list.append(follow.following)

            user_following_following = Follow.objects.filter(created_by=user_followings[0].following)
            if user_following_following:
                for follow in user_following_following:
                    if follow.following not in user_followings_users_list:
                        suggestions.append(follow.following)
                        continue
            user_following_followers = Follow.objects.filter(following=user_followings[0].following)
            if user_following_followers:
                for follow in user_following_followers:
                    if follow.created_by not in user_followings_users_list:
                        suggestions.append(follow.created_by)
                        continue
        if user_followers:
            user_followers_following = Follow.objects.filter(following=user_followers[0].created_by)
            if user_followers_following:
                for follow in user_followers_following:
                    if follow.created_by not in user_followings_users_list:
                        suggestions.append(follow.created_by)
                        continue
            user_followers_followers = Follow.objects.filter(created_by=user_followings[0].created_by)
            if user_followers_followers:
                for follow in user_followers_followers:
                    if follow.following not in user_followings_users_list:
                        suggestions.append(follow.following)
                        continue

        if not suggestions:
            suggest_user = User.objects.filter(is_staff=False, is_active=True).exclude(id=user.id).first()
            suggestions.append(suggest_user)
        suggestion = set(user.username for user in suggestions)  # Creates a set of unique usernames
        data = {
            "suggestions": list(suggestion)
        }
        return Response(data)
