import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from tests import factories as f
from tests.utils import _test_authenticate_user

pytestmark = pytest.mark.django_db


def test_create_post_with_101_character_caption(api_client) -> None:
    """
    Test the create post API
    """
    _test_authenticate_user(api_client, "username", "password123")
    payload = {
        "image": "image.jpeg",
        "caption": "Lorem ipsum dolor sit amet, "
        "consectetur adipiscing elit. "
        "Vivamus lacinia odio vitae vestibulum.",
    }

    response = api_client.post("/imageshare/posts", data=payload)
    assert response.status_code == 400


def test_timestamp_on_created_post(api_client) -> None:
    """
    Test the create post is created with a time stamp
    """
    _test_authenticate_user(api_client, "username", "password123")
    payload = {"caption": "Lorem ipsum dolor sit amet"}
    test_image = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
        content_type="image/jpeg",
    )
    payload["image"] = test_image  # Add the image file to the payload

    response = api_client.post("/imageshare/posts", data=payload, format="multipart")

    assert response.status_code == 201, f"Post creation failed: {response.data}"
    assert response.data["created_at"] is not None


def test_publish_post_created_by_authenticated_user(api_client) -> None:
    """
    Test the publish post by authenticated user
    """
    auth_user = _test_authenticate_user(api_client, "username", "password123")
    post = f.create_post(created_by=auth_user)
    response = api_client.get(f"/imageshare/posts/publish?post_id={post.id}")
    assert response.status_code == 200
    assert response.data["shareable_link"] is not None


def test_publish_post_created_by_another_user(api_client) -> None:
    """
    Test the publish post by another user
    """
    _test_authenticate_user(api_client, "username", "password123")
    user = f.create_user()
    post = f.create_post(created_by=user)
    response = api_client.get(f"/imageshare/posts/publish?post_id={post.id}")
    assert response.status_code == 403


def test_get_posts(api_client) -> None:
    auth_user = _test_authenticate_user(api_client, "username", "password123")
    user1 = f.create_user(username="user1")
    user2 = f.create_user(username="user2")
    user3 = f.create_user(username="user3")
    f.create_post(created_by=user1, caption="test caption 1")
    f.create_post(created_by=user2, caption="test caption 2")
    f.create_post(created_by=user3, caption="test caption 3")
    f.create_follow(created_by=auth_user, following=user1)
    f.create_follow(created_by=auth_user, following=user2)

    """
    Test list posts by users followed by the authenticated user
    """
    response = api_client.get("/imageshare/posts/followed")
    assert response.status_code == 200
    assert response.data["count"] == 2

    """
    Test list posts by all users
    """
    response = api_client.get("/imageshare/posts")
    assert response.status_code == 200
    assert response.data["count"] == 3

    """
    Test search for post by caption from all users posts list 
    """
    response = api_client.get("/imageshare/posts?search=2")
    assert response.status_code == 200
    assert response.data["count"] == 1
