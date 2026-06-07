"""
HTTP-layer tests for the agent router — SSE endpoint and history clear.

Tests only the HTTP boundary: auth enforcement, request validation, and
response shape. The actual SSE generator (``_sse_generator``) is mocked so
no real agent runs or Google Sheets calls occur.

A module-scoped ``client`` fixture is used (separate from the session-scoped
one in ``conftest.py``) to ensure the Azure OpenAI env vars are set before
the agent router is imported.
"""

import os

# Set agent env vars before the agent package is imported
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

from unittest.mock import MagicMock, patch

import pytest


async def _fake_sse_gen(*args, **kwargs):
    """
    Minimal SSE generator that yields one text event and a done sentinel.

    Used to mock ``_sse_generator`` so tests receive a well-formed stream
    without running a real agent.
    """
    yield 'data: {"type": "text", "content": "Hello"}\n\n'
    yield 'data: {"type": "done"}\n\n'


@pytest.fixture(scope="module")
def client():
    """Module-scoped test client with Sheets mocked."""
    with patch("api.sheets.sheets_client.get_main_sheet", return_value=MagicMock()):
        from api.main import app
        from fastapi.testclient import TestClient
        with TestClient(app) as c:
            yield c


@pytest.fixture(scope="module")
def auth_headers():
    """Module-scoped bearer token headers for user_id=1."""
    from api.auth import create_jwt
    token = create_jwt("test@example.com", 1)
    return {"Authorization": f"Bearer {token}"}


# ── POST /agent/chat ─────────────────────────────────────────────────────────

class TestChatEndpoint:
    def test_requires_auth(self, client):
        resp = client.post("/agent/chat", json={"message": "hi", "session_id": "s1"})
        assert resp.status_code == 403

    def test_returns_422_for_missing_fields(self, client, auth_headers):
        resp = client.post("/agent/chat", json={}, headers=auth_headers)
        assert resp.status_code == 422

    def test_returns_422_for_missing_session_id(self, client, auth_headers):
        resp = client.post("/agent/chat", json={"message": "hi"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_returns_422_for_missing_message(self, client, auth_headers):
        resp = client.post("/agent/chat", json={"session_id": "s1"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_returns_event_stream_with_auth(self, client, auth_headers):
        with patch("api.routers.agent._sse_generator", side_effect=_fake_sse_gen):
            resp = client.post(
                "/agent/chat",
                json={"message": "hello", "session_id": "sess-1"},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

    def test_sse_body_contains_events(self, client, auth_headers):
        with patch("api.routers.agent._sse_generator", side_effect=_fake_sse_gen):
            resp = client.post(
                "/agent/chat",
                json={"message": "hello", "session_id": "sess-2"},
                headers=auth_headers,
            )
        assert b"data:" in resp.content
        assert b'"type": "text"' in resp.content


# ── DELETE /agent/history ────────────────────────────────────────────────────

class TestClearHistoryEndpoint:
    def test_requires_auth(self, client):
        resp = client.delete("/agent/history")
        assert resp.status_code == 403

    def test_returns_204_with_auth(self, client, auth_headers):
        with patch("api.routers.agent.clear_all_sessions") as mock_clear:
            resp = client.delete("/agent/history", headers=auth_headers)
        assert resp.status_code == 204
        mock_clear.assert_called_once()
