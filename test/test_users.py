from passlib.context import CryptContext
from starlette import status
from starlette.testclient import TestClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from ..main import app

client = TestClient(app)


def test_get_active_user(test_user):
    response = client.get("/user/active_user")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name
    assert data["role"] == test_user.role
    assert data["is_active"] == test_user.is_active


def test_change_password(test_user):
    payload = {
        "old_password": "oldpassword",
        "new_password": "Newpass1!"
    }

    response = client.put("/user/change_password", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Password changed successfully"
