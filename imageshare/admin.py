# Register your models here.
from django.contrib import admin
from .models import Post, Like, Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["id", "created_by", "following"]
    list_filter = ["created_by", "following"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "created_by", "image", "caption"]
    list_filter = ["created_by"]
    search_fields = ["id", "caption"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "liked_by"]
