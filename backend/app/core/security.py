from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload(sub=payload.get("sub"), exp=payload.get("exp"))
    except JWTError:
        return None