from rest_framework import serializers
from .models import User
from imageshare.serializers import PostSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Add the password field
    posts = serializers.SerializerMethodField()
    follows = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'password',
                  'posts', 'follows']
        extra_kwargs = {
            'password': {'write_only': True}, # Ensure it's only used for write operations
            'posts': {'read_only': True},
            'follows': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')  # Remove password from validated_data
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_posts(self, obj):
        posts = obj.posts.all()

        return {
            "posts_count": posts.count(),
            "posts_created": PostSerializer(posts, many=True).data
        }

    def get_follows(self, obj):
        followers = obj.followers.all().values_list('created_by__username', flat=True)
        followings = obj.followings.all().values_list('following__username', flat=True)

        return {
            "followings_count": followings.count(),
            "followers_count": followers.count(),
            "followings": list(followings),
            "followers": list(followers)
        }
