"""Tests for POST /auth/login, JWT utilities, and get_current_user dependency."""
from unittest.mock import patch

import pytest
from fastapi import HTTPException


STORED_CREDS = [
    {"user_id": 1, "email": "owner@example.com", "password": "secret"},
    {"user_id": 2, "email": "friend@example.com", "password": "hunter2"},
]


def _find_user(email: str):
    for user in STORED_CREDS:
        if user["email"].lower() == email.strip().lower():
            return user
    return None


class TestLoginEndpoint:
    def test_login_success(self, client):
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "owner@example.com", "password": "secret"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_success_token_contains_user_id(self, client):
        from api.auth import verify_jwt
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "owner@example.com", "password": "secret"})
        token = resp.json()["access_token"]
        user_id = verify_jwt(token)
        assert user_id == 1

    def test_login_second_user(self, client):
        from api.auth import verify_jwt
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "friend@example.com", "password": "hunter2"})
        assert resp.status_code == 200
        assert verify_jwt(resp.json()["access_token"]) == 2

    def test_login_email_case_insensitive(self, client):
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "OWNER@Example.COM", "password": "secret"})
        assert resp.status_code == 200

    def test_login_wrong_password(self, client):
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "owner@example.com", "password": "wrong"})
        assert resp.status_code == 401

    def test_login_wrong_email(self, client):
        with patch("api.auth.find_user", side_effect=_find_user):
            resp = client.post("/auth/login", json={"email": "other@example.com", "password": "secret"})
        assert resp.status_code == 401

    def test_login_sheet_error(self, client):
        with patch("api.auth.find_user", side_effect=Exception("Sheets unavailable")):
            resp = client.post("/auth/login", json={"email": "owner@example.com", "password": "secret"})
        assert resp.status_code == 500


class TestJWTUtilities:
    def test_create_and_verify_jwt_returns_user_id(self):
        from api.auth import create_jwt, verify_jwt
        token = create_jwt("test@example.com", 42)
        user_id = verify_jwt(token)
        assert user_id == 42

    def test_verify_jwt_invalid_token_raises_401(self):
        from api.auth import verify_jwt
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_verify_jwt_missing_user_id_claim_raises_401(self):
        """A correctly-signed token without a user_id claim is rejected with 401, not 500."""
        import os

        from jose import jwt as jose_jwt

        from api.auth import verify_jwt

        token = jose_jwt.encode({"sub": "test@example.com"}, os.environ["JWT_SECRET"], algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(token)
        assert exc_info.value.status_code == 401

    def test_verify_jwt_non_numeric_user_id_raises_401(self):
        """A user_id claim that cannot be coerced to int is rejected with 401."""
        import os

        from jose import jwt as jose_jwt

        from api.auth import verify_jwt

        token = jose_jwt.encode(
            {"sub": "test@example.com", "user_id": "not-a-number"},
            os.environ["JWT_SECRET"],
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(token)
        assert exc_info.value.status_code == 401


class TestProtectedRoute:
    def test_no_auth_header_returns_401(self, client):
        resp = client.get("/settings")
        assert resp.status_code == 401

    def test_bad_token_returns_401(self, client):
        resp = client.get("/settings", headers={"Authorization": "Bearer bad.token.here"})
        assert resp.status_code == 401
