
import pytest

from . import factories as f



pytestmark = pytest.mark.django_db


def _test_authenticate_user(api_client, username, password) -> object:
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
    return user

