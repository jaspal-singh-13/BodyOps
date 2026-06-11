"""
JWT creation/verification and login endpoint.

Auth flow:
    1. Client POSTs ``{email, password}`` to ``/auth/login``.
    2. ``login()`` looks up the credential row matching the email in the Auth Sheet.
    3. Credentials are compared in plain text (owner-managed sheet).
    4. On success, a signed JWT containing ``user_id`` is returned.
    5. Every protected route extracts ``user_id`` via the ``get_current_user``
       FastAPI dependency, which calls ``verify_jwt`` on the bearer token.

Token lifetime is controlled by ``JWT_EXPIRE_MINUTES`` (default: 10080 = 7 days).
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from .logger import get_logger
from .sheets.auth_sheet import find_user  # pure in-memory after startup

logger = get_logger("auth")

# auto_error=False so we can return 401 (Unauthorized) instead of 403 (Forbidden)
# when no Authorization header is provided.
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Response body returned on successful login."""

    access_token: str
    token_type: str = "bearer"


def create_jwt(email: str, user_id: int) -> str:
    """
    Create a signed JWT containing the user's email and integer ID.

    The token expires after ``JWT_EXPIRE_MINUTES`` minutes (default 7 days).
    Algorithm and secret are read from env vars ``JWT_ALGORITHM`` / ``JWT_SECRET``.

    Args:
        email: The authenticated user's email address (stored in ``sub`` claim).
        user_id: Integer user ID from the Auth Sheet (stored in ``user_id`` claim).

    Returns:
        Signed JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.environ.get("JWT_EXPIRE_MINUTES", 10080))
    )
    return jwt.encode(
        {"sub": email, "user_id": user_id, "exp": expire},
        os.environ["JWT_SECRET"],
        algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
    )


def verify_jwt(token: str) -> int:
    """
    Decode and verify a JWT, returning the ``user_id`` claim.

    Args:
        token: Raw JWT string (without the "Bearer " prefix).

    Returns:
        Integer ``user_id`` from the token payload.

    Raises:
        HTTPException(401): If the token is invalid, expired, or missing ``user_id``.
    """
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET"],
            algorithms=[os.environ.get("JWT_ALGORITHM", "HS256")],
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("missing user_id")
        return int(user_id)
    except JWTError as e:
        segments = len(token.split(".")) if token else 0
        logger.warning(
            "JWT verification failed: %s (segments=%d, token_len=%d)",
            e, segments, len(token),
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> int:
    """
    FastAPI dependency that extracts and verifies the bearer token.

    Inject this into any route that requires authentication::

        @router.get("/protected")
        async def handler(user_id: int = Depends(get_current_user)):
            ...

    Returns:
        Authenticated user's integer ID.

    Raises:
        HTTPException(401): If the token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_jwt(credentials.credentials)


async def login(body: LoginRequest) -> TokenResponse:
    """
    Validate credentials against the Auth Sheet and return a JWT on success.

    Looks up the credential row matching the email (case-insensitive) via
    ``find_user()``. Compares the password in plain text.

    Args:
        body: ``LoginRequest`` containing ``email`` and ``password``.

    Returns:
        ``TokenResponse`` with a signed JWT bearer token.

    Raises:
        HTTPException(500): If the Auth Sheet cannot be read.
        HTTPException(401): If email or password is incorrect.
    """
    logger.info("Login attempt: %s", body.email)
    try:
        user = find_user(body.email)
    except Exception as e:
        logger.error("Auth Sheet read failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Auth Sheet error: {e}")

    if user is None or body.password != user["password"]:
        logger.warning("Login failed (bad credentials): %s", body.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Login successful: %s (user_id=%s)", user["email"], user["user_id"])
    return TokenResponse(access_token=create_jwt(user["email"], user["user_id"]))
