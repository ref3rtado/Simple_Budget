"""
Tests for the guest / "Preview App" login flow.

Clicking "Preview App" on the front end POSTs to /user/create_temp_user,
which should create a temp account, log it into the session, and redirect
(via the HX-Redirect header) to GET /dashboard0. That page should then
render with is_temp_user=True in its template context, which surfaces as
the "Temporary session" warning banner (see dashboard.html).

NOTE: create_temp_user currently references an undefined `request` name to
reach the session, and the app never registers Starlette's SessionMiddleware,
so guest login currently 500s. These tests describe the intended, successful
behavior and are expected to fail until that bug is fixed elsewhere.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.model.database import Base, get_db

DEV_INVITE_CODE = "TEST-DEV-CODE"


@pytest.fixture
def client(monkeypatch):
    """
    TestClient wired to a fresh, isolated in-memory SQLite database.

    The temp account created during a test only ever lives in this
    per-test engine and is dropped/disposed at teardown, so the guest
    account never persists past the test - no explicit "delete the temp
    user" step (and the coupling to crud/db internals that would require)
    is needed.
    """
    monkeypatch.setenv("DEV-INVITE-CODE", DEV_INVITE_CODE)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_create_temp_user_logs_in_and_redirects_to_dashboard(client):
    """POST /user/create_temp_user should succeed and tell the frontend
    (via HX-Redirect) to load /dashboard0 for the newly logged-in guest."""
    response = client.post("/user/create_temp_user")

    assert response.status_code == 200
    assert response.headers.get("HX-Redirect") == "/dashboard0"


def test_dashboard_renders_as_temp_user_after_guest_login(client):
    """After the guest login, GET /dashboard0 should render successfully
    with is_temp_user=True, shown as the "Temporary session" banner that
    dashboard.html only renders when that context value is True."""
    client.post("/user/create_temp_user")

    response = client.get("/dashboard0")

    assert response.status_code == 200
    assert "Temporary session" in response.text
