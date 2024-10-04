from rest_framework import serializers
from .models import Post, Follow


class PostSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'image', 'caption', 'created_by', 'created_at', 'modified_at',
                  'likes_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'modified_at', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()  # Return the count of likes for the post
    

class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['id', 'created_by', 'following', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

