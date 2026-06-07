"""JWT creation/verification and login endpoint."""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from .logger import get_logger
from .sheets.auth_sheet import get_credentials

logger = get_logger("auth")
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_jwt(email: str, user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.environ.get("JWT_EXPIRE_MINUTES", 10080))
    )
    return jwt.encode(
        {"sub": email, "user_id": user_id, "exp": expire},
        os.environ["JWT_SECRET"],
        algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
    )


def verify_jwt(token: str) -> int:
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
        logger.warning("JWT verification failed: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    return verify_jwt(credentials.credentials)


async def login(body: LoginRequest) -> TokenResponse:
    logger.info("Login attempt: %s", body.email)
    try:
        stored = get_credentials()
    except Exception as e:
        logger.error("Auth Sheet read failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Auth Sheet error: {e}")

    if body.email != stored.get("email") or body.password != stored.get("password"):
        logger.warning("Login failed (bad credentials): %s", body.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("Login successful: %s (user_id=%s)", body.email, stored["user_id"])
    return TokenResponse(access_token=create_jwt(body.email, stored["user_id"]))
