import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def create_google_oauth_state(redirect_to: Optional[str] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {
        "sub": "google-oauth",
        "nonce": secrets.token_urlsafe(32),
        "type": "google_oauth_state",
        "exp": expire,
    }
    if redirect_to:
        payload["redirect_to"] = redirect_to
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def google_oauth_state_failure(
    token: Optional[str], cookie_state: Optional[str] = None
) -> Optional[str]:
    """Return a safe diagnostic reason, or None when state and cookie are valid."""
    if not token:
        return "state_missing"
    if not cookie_state:
        return "cookie_missing"
    if not secrets.compare_digest(token, cookie_state):
        return "cookie_mismatch"

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        return "expired"
    except JWTError as error:
        if "signature" in str(error).lower():
            return "bad_signature"
        return "invalid_jwt"

    if payload.get("type") != "google_oauth_state":
        return "wrong_type"
    if payload.get("sub") != "google-oauth":
        return "wrong_subject"
    if not isinstance(payload.get("nonce"), str) or not payload["nonce"]:
        return "invalid_nonce"
    return None


def validate_google_oauth_state(token: str, cookie_state: Optional[str] = None) -> bool:
    """Require a valid signed state JWT and the exact matching browser cookie."""
    return google_oauth_state_failure(token, cookie_state) is None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    trial_ends_at = user.trial_ends_at
    if trial_ends_at is not None and trial_ends_at.tzinfo is None:
        trial_ends_at = trial_ends_at.replace(tzinfo=timezone.utc)
    if not user.is_superuser and trial_ends_at and trial_ends_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Your 14-day free trial has ended")

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser and current_user.role not in {
        UserRole.OWNER,
        UserRole.ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user