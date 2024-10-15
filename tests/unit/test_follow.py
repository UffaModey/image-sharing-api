import pytest

from tests import factories as f
from tests.utils import _test_authenticate_user

pytestmark = pytest.mark.django_db

def test_follow_self(api_client) -> None:
    """
    Test follow self
    """
    user = _test_authenticate_user(api_client, 'username', 'password123')
    payload = {
        "following": str(user.id)  }

    response = api_client.post("/imageshare/follow", data=payload)
    assert response.status_code == 400


def test_follow_an_already_followed_user(api_client) -> None:
    """
    Test follow an already followed user
    """
    auth_user = _test_authenticate_user(api_client, 'username', 'password123')
    user = f.create_user()
    f.create_follow(created_by=auth_user, following=user)
    payload = {
        "following": str(user.id)  }

    response = api_client.post("/imageshare/follow", data=payload)
    assert response.status_code == 400

@pytest.mark.django_db(transaction=True)
def test_mutual_followers(api_client) -> None:
    """
        Test mutual followers
    """
    auth_user = _test_authenticate_user(api_client, 'username', 'password123')
    user = f.create_user()
    mutual_follower = f.create_user(username="mutual_follower")
    auth_user_follower = f.create_user(username="auth_user_follower")
    user_follower = f.create_user(username="user_follower")
    f.create_follow(created_by=mutual_follower, following=user)
    f.create_follow(created_by=auth_user_follower, following=auth_user)
    f.create_follow(created_by=user_follower, following=user)
    f.create_follow(created_by=mutual_follower, following=auth_user)
    response = api_client.get(f"/imageshare/mutual-followers/{str(user.id)}/")
    assert response.status_code == 200
    assert mutual_follower.username in response.data["mutual_followers"]
    assert len(response.data["mutual_followers"]) == 1


@pytest.mark.django_db(transaction=True)
def test_auth_user_not_in_follow_suggestions(api_client) -> None:
    """
        Test that the authenticated user is not listed as a follow suggestion
    """
    auth_user = _test_authenticate_user(api_client, 'username', 'password123')
    user = f.create_user()
    mutual_follower = f.create_user(username="mutual_follower")
    auth_user_follower = f.create_user(username="auth_user_follower")
    user_follower = f.create_user(username="user_follower")
    f.create_follow(created_by=mutual_follower, following=user)
    f.create_follow(created_by=auth_user_follower, following=auth_user)
    f.create_follow(created_by=user_follower, following=user)
    f.create_follow(created_by=mutual_follower, following=auth_user)
    response = api_client.get("/imageshare/follow-suggestions/")
    assert response.status_code == 200
    assert response.data["suggestions"] is not None
    assert auth_user.username not in response.data["suggestions"]
