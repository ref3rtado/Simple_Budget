from fastapi.testclient import TestClient
from main import app

def test_app_starts_without_exceptions():
    """
    To pass this test, the login route must be accessible and
    MySQL service must be running.
    """
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200, "Application failed to start."