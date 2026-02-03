# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings


# Password hasher
ph = PasswordHasher()


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return ph.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None
