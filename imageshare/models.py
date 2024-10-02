from django.conf import settings
from django.db import models

from isa.models import TimeStampedUUIDModel

from users.models import User


class Post(TimeStampedUUIDModel):
    """
        Model representing posts
    """
    image = models.ImageField(upload_to='posts/', help_text='Image uploaded by the user')
    caption = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE,
                                help_text='User who created the post')

    class Meta:
        verbose_name_plural = "Posts"
        ordering = ['created_at']

    def __str__(self):
        return f'{self.created_by.username} - {self.caption[:30]}...'

class Like(TimeStampedUUIDModel):
    """
        Model representing likes on a post
    """
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE,
                             help_text='Post that was liked')
    liked_by = models.ForeignKey(User, related_name='liked_posts', on_delete=models.CASCADE,
                                   help_text='User who liked the post')

    class Meta:
        verbose_name_plural = "Likes"
        ordering = ['created_at']

    def __str__(self):
        return f'{self.post.caption[:30]}... - {self.liked_by.username}'


class Follow(TimeStampedUUIDModel):
    """
        Model representing the following relationship between users
    """
    created_by = models.ForeignKey(User, related_name='followings', on_delete=models.CASCADE,
                             help_text='User who is following another user')
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE,
                                  help_text='User who is being followed')

    class Meta:
        verbose_name_plural = "Follows"
        ordering = ['created_at']

    def __str__(self):
        return f'{self.created_by.username} followed {self.following.username}'
