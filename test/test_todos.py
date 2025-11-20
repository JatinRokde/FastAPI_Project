from starlette import status
from starlette.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_get_todo(test_user, test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK

    todos = response.json()

    todo = todos[0]

    assert todo["title"] == "Test Todo"
    assert todo["description"] == "Test Description"
    assert todo["priority"] == 3
    assert todo["complete"] is False
    assert todo["user_id"] == test_user.id
