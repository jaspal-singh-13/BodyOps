"""
Shared pytest fixtures for all test modules.

Sets required environment variables *before* any ``api.*`` import so that
module-level code (e.g. ``load_dotenv`` in ``api/main.py``) doesn't error
due to missing config.

Fixtures:
    client       — session-scoped FastAPI ``TestClient`` with Sheets mocked.
    auth_headers — session-scoped ``Authorization: Bearer`` header dict
                   containing a valid JWT for ``user_id=1``.
"""

import os

# Set env vars before any api.* import to satisfy module-level checks
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """
    Session-scoped FastAPI test client with ``get_main_sheet`` mocked.

    Mocking at the ``sheets_client`` level prevents any real Google API calls
    during tests. The mock returns a ``MagicMock`` that individual tests can
    further configure via ``patch`` context managers.
    """
    with patch("api.sheets.sheets_client.get_main_sheet", return_value=MagicMock()):
        from api.main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture(scope="session")
def auth_headers():
    """
    Session-scoped bearer token headers for ``user_id=1``.

    Creates a real JWT (signed with the test secret) so the ``get_current_user``
    dependency resolves without mocking the auth layer.

    Returns:
        Dict with a single key ``"Authorization"`` containing a valid
        ``Bearer <token>`` string for ``user_id=1``.
    """
    from api.auth import create_jwt
    token = create_jwt("test@example.com", 1)
    return {"Authorization": f"Bearer {token}"}
