from starlette import status
from starlette.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_admin_get_all_todos(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK

    todo = response.json()[0]
    assert todo["title"] == "Test Todo"
    assert todo["description"] == "Test Description"


def test_admin_delete_todo(test_todo):
    todo_id = test_todo.id

    response = client.delete(f"/admin/todos/{todo_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # verify deletion
    verify = client.get("/admin/todos")
    todos = verify.json()
    assert len(todos) == 0