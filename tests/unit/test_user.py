import logging
import pytest

from tests import factories as f
from tests.utils import _test_authenticate_user

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


pytestmark = pytest.mark.django_db


def test_create_user(api_client) -> None:
    """
    Test the create user API
    :param api_client:
    :return: None
    """
    user_data = {
        "username": "newuser",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }

    # test create a user
    response = api_client.post("/user/", data=user_data)
    user_id = response.data["id"]
    logger.info(f"Created a user with id: {user_id}")
    logger.info(f"Response: {response.data}")
    assert response.status_code == 201
    assert response.data["username"] == user_data["username"]


def test_create_user_with_existing_username(api_client) -> None:
    """
    Test create a user with an existing username
    """
    f.create_user(username="username", email='user@foo.com', password="password")
    user_data = {
        "username": "username",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }

    response = api_client.post("/user/", data=user_data)
    assert response.status_code == 400


def test_create_user_with_existing_email(api_client) -> None:
    """
    Test create a user with an existing email
    """
    f.create_user(username="username1", email='newuser@example.com', password="password")
    user_data = {
        "username": "username",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }

    response = api_client.post("/user/", data=user_data)
    assert response.status_code == 400


def test_get_user_profile(api_client) -> None:
    """
    Test get a user's profile
    """
    user = _test_authenticate_user(api_client, 'username', 'password123')

    response = api_client.get(f"/user/{user.id}", format="json")
    assert response.status_code == 200, "Failed to retrieve user profile"
    logger.info(f"Read user with id: {user.id}")
    logger.info(f"Response: {response.data}")
    assert response.data["username"] == user.username


def test_list_users(api_client) -> None:
    """
    Test listing all users
    """
    _test_authenticate_user(api_client, 'username', 'password123')
    f.create_user()

    response = api_client.get(f"/user/", format="json")
    assert response.status_code == 200, "Failed to list users"
    assert response.data["count"] == 2
