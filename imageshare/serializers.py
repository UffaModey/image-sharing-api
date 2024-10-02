from rest_framework import serializers
from .models import Post, Follow



class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'image', 'caption', 'created_by', 'created_at', 'modified_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'modified_at']


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['id', 'created_by', 'following', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

