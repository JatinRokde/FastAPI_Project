from starlette import status
from starlette.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'ok'}
