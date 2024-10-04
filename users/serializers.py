from rest_framework import serializers
from .models import User
from imageshare.serializers import PostSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Add the password field
    posts_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'password',
                  'posts_count', 'posts']
        extra_kwargs = {
            'password': {'write_only': True}, # Ensure it's only used for write operations
            'posts_count': {'read_only': True},
            'posts': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')  # Remove password from validated_data
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_posts(self, obj):
        posts = obj.posts.all()
        return PostSerializer(posts, many=True).data
