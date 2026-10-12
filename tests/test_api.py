import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.auth import get_user

client = TestClient(main.app)
calls = {}


def fake_agent(task, **kwargs):
    calls.update(kwargs)
    return {"answer": "ok", "sources": ["a.py"]}


@pytest.fixture
def logged_in():
    main.app.dependency_overrides[get_user] = lambda: "test-uid"
    yield
    main.app.dependency_overrides.clear()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_login_required():
    assert client.get("/repos").status_code == 401


def test_explain_scopes_repo_to_user(monkeypatch, logged_in):
    monkeypatch.setattr(main, "explain", fake_agent)
    r = client.post("/explain", json={"task": "explain add_url_rule", "repo": "flask"})
    assert r.status_code == 200
    assert calls["repo"] == "test-uid__flask"   # Retrieval is restricted to the authenticated user's data.


def test_ingest_rejects_non_github_url(logged_in):
    assert client.post("/ingest", json={"url": "file:///etc/passwd"}).status_code == 400


def test_repo_is_required(logged_in):
    assert client.post("/ask", json={"question": "hello there"}).status_code == 422
