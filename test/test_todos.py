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


def test_get_single_todo(test_user, test_todo):
    response = client.get(f"/todos/{test_todo.id}")

    assert response.status_code == status.HTTP_200_OK

    todo = response.json()

    assert todo["id"] == test_todo.id
    assert todo["title"] == test_todo.title
    assert todo["description"] == test_todo.description
    assert todo["priority"] == test_todo.priority
    assert todo["complete"] == test_todo.complete
    assert todo["user_id"] == test_user.id


def test_add_todo(test_user):
    payload = {
        'title': 'New Todo',
        'description': 'New Description',
        'priority': 4,
        'complete': False
    }

    response = client.post("/todos/add_todo", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    get_todo = client.get(f"/todos")
    todos = get_todo.json()
    created_todo = todos[-1]
    assert created_todo["title"] == payload["title"]
    assert created_todo["description"] == payload["description"]
    assert created_todo["priority"] == payload["priority"]
    assert created_todo["complete"] == payload["complete"]


def test_update_todo(test_todo):
    todo_id = test_todo.id
    updated_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "priority": 5,
        "complete": True
    }

    response = client.put(f"/todos/{todo_id}", json=updated_payload)

    assert response.status_code == status.HTTP_200_OK
    get_todo = client.get(f"/todos/{todo_id}")
    todos = get_todo.json()
    assert todos["title"] == updated_payload["title"]
    assert todos["description"] == updated_payload["description"]
    assert todos["priority"] == updated_payload["priority"]
    assert todos["complete"] == updated_payload["complete"]
