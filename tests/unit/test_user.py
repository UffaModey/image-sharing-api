import logging
import pytest

from tests import factories as f

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


pytestmark = pytest.mark.django_db


def _test_authenticate_user(api_client, username, password) -> dict:
    """
    Helper function to authenticate a user and return an access token.
    """
    user = f.create_user(username=username, email='user@foo.com', password=password)

    payload = {
        "username": username,
        "password": password
    }
    response_create = api_client.post("/api/token/", data=payload)
    assert response_create.status_code == 200, "Authentication failed"

    # Set the Authorization header with the token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response_create.data["access"]}')
    return {"user_id": user.id,
            "username": user.username}


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
    response_create = api_client.post("/user/", data=user_data)
    user_id = response_create.data["id"]
    logger.info(f"Created a user with id: {user_id}")
    logger.info(f"Response: {response_create.data}")
    assert response_create.status_code == 201
    assert response_create.data["username"] == user_data["username"]


def test_create_user_with_existing_username(api_client) -> None:
    f.create_user(username="username", email='user@foo.com', password="password")
    user_data = {
        "username": "username",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }

    # test create a user
    response_create = api_client.post("/user/", data=user_data)
    assert response_create.status_code == 400


def test_create_user_with_existing_email(api_client) -> None:
    f.create_user(username="username1", email='newuser@example.com', password="password")
    user_data = {
        "username": "username",
        "password": "newpassword123",
        "email": "newuser@example.com"
    }

    # test create a user
    response_create = api_client.post("/user/", data=user_data)
    assert response_create.status_code == 400


def test_get_user_profile(api_client) -> None:

    # Authenticate the user and get the access token
    user = _test_authenticate_user(api_client, 'username', 'password123')

    # Test get a user's profile
    response_read = api_client.get(f"/user/{user['user_id']}", format="json")
    assert response_read.status_code == 200, "Failed to retrieve user profile"
    logger.info(f"Read user with id: {user['user_id']}")
    logger.info(f"Response: {response_read.data}")
    assert response_read.data["username"] == user['username']


def test_list_users(api_client) -> None:
    """Test listing all users"""
    # Authenticate the user and get the access token
    _test_authenticate_user(api_client, 'username', 'password123')
    f.create_user()

    # Test list users
    response_read = api_client.get(f"/user/", format="json")
    assert response_read.status_code == 200, "Failed to list users"
    assert response_read.data["count"] == 2
