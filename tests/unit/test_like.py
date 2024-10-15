
import pytest

from tests import factories as f
from tests.utils import _test_authenticate_user


pytestmark = pytest.mark.django_db


def test_like_post(api_client) -> None:
    """
    Test like a post
    """
    auth_user = _test_authenticate_user(api_client, 'username', 'password123')
    post = f.create_post()
    response = api_client.post(f"/imageshare/post/{post.id}/like")
    assert response.status_code == 201

    response = api_client.get(f"/imageshare/post/{post.id}/like")
    assert response.status_code == 200
    assert response.data["total_likes"] == 1
    assert auth_user.username in response.data["liked_by"]


def test_like_an_already_liked_post(api_client) -> None:
    """
    Test like a post that the authenticated user has already liked
    """
    auth_user = _test_authenticate_user(api_client, 'username', 'password123')
    post = f.create_post()
    f.create_like(post=post, liked_by=auth_user)
    response = api_client.post(f"/imageshare/post/{post.id}/like")
    assert response.status_code == 400
