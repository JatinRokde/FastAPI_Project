import os

from jose import jwt
from passlib.context import CryptContext
from starlette import status
from starlette.testclient import TestClient

from ..main import app

client = TestClient(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def test_login_success(test_user):
    payload = {
        "username": test_user.username,
        "password": "oldpassword"
    }

    response = client.post("/auth/token", data=payload)
    assert response.status_code == status.HTTP_200_OK

    token = response.json()["access_token"]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded["sub"] == test_user.username
    assert decoded["id"] == test_user.id


def test_get_current_user(test_user):
    login_data = {
        "username": test_user.username,
        "password": "oldpassword"
    }
    login_res = client.post("/auth/token", data=login_data)
    token = login_res.json()["access_token"]

    response = client.get(
        "/user/active_user",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username
