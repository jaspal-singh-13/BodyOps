"""Shared fixtures for all tests. Sets env vars before any api.* import."""
import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    with patch("api.sheets.sheets_client.get_main_sheet", return_value=MagicMock()):
        from api.main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture(scope="session")
def auth_headers():
    from api.auth import create_jwt
    token = create_jwt("test@example.com", 1)
    return {"Authorization": f"Bearer {token}"}
