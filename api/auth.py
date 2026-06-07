"""JWT creation/verification and login endpoint."""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from .sheets.auth_sheet import get_credentials

bearer_scheme = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_jwt(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.environ.get("JWT_EXPIRE_MINUTES", 10080))
    )
    return jwt.encode(
        {"sub": email, "exp": expire},
        os.environ["JWT_SECRET"],
        algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
    )


def verify_jwt(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET"],
            algorithms=[os.environ.get("JWT_ALGORITHM", "HS256")],
        )
        email: str = payload.get("sub", "")
        if not email:
            raise ValueError("missing sub")
        return email
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return verify_jwt(credentials.credentials)


async def login(body: LoginRequest) -> TokenResponse:
    try:
        stored = get_credentials()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth Sheet error: {e}")

    if body.email != stored.get("email") or body.password != stored.get("password"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(access_token=create_jwt(body.email))
