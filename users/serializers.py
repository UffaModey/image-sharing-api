from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Add the password field
    posts = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "password",
            "posts",
            "followings",
            "followers",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            },  # Ensure it's only used for write operations
            "posts": {"read_only": True},
            "followings": {"read_only": True},
            "followers": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")  # Remove password from validated_data
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_posts(self, obj):
        return obj.posts.count()

    def get_followers(self, obj):
        return obj.followers.count()

    def get_followings(self, obj):
        return obj.followings.count()
