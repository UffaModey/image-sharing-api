"""
Helpers to create dynamic model instances for testing purposes.

Usages:
>>> from tests import factories as f
>>>
>>> user = f.create_user(first_name="Robert", last_name="Downey")  # creates single instance of user
>>> users = f.create_user(n=5, is_active=False)  # creates 5 instances of user

There is a bit of magic going on behind the scenes with `G` method from https://django-dynamic-fixture.readthedocs.io/
"""

# Standard Library
import uuid

# Third Party Stuff
from django.apps import apps
from django.conf import settings
from django_dynamic_fixture import G

from imageshare.models import Post, Like, Follow


def create_user(username=str(uuid.uuid4()), **kwargs):
    """Create a user along with their dependencies."""
    User = apps.get_model(settings.AUTH_USER_MODEL)
    user = G(User, username=username, **kwargs)
    user.set_password(kwargs.get("password", "test"))
    user.save()
    return user


def create_post(**kwargs):
    """Create post"""
    return G(Post, **kwargs)


def create_like(**kwargs):
    """Create like"""
    return G(Like, **kwargs)


def create_follow(**kwargs):
    """Create follow"""
    return G(Follow, **kwargs)
