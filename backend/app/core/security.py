from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_reset_token(raw_token: str) -> str:
    """
    SHA-256 (not bcrypt) is intentional here: reset tokens are already
    high-entropy random strings (secrets.token_urlsafe), so we don't need
    bcrypt's slow, salted hashing — we need a fast, deterministic digest we
    can look up by by equality in the DB. Storing the raw token would mean
    anyone with read access to the database (backup leak, SQL injection,
    curious DBA) could take over any account mid-reset; hashing it closes
    that off while keeping the lookup simple.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
