from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import get_settings
from .models import User, RefreshToken
from .schemas import TokenData
import secrets

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(db: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_revoked=False
    )
    db.add(refresh_token)
    db.commit()
    return token

def verify_token(token: str, credentials_exception) -> TokenData:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        username = payload.get("username")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        raise credentials_exception

def revoke_refresh_token(db: Session, token: str) -> bool:
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if refresh_token:
        refresh_token.is_revoked = True
        db.commit()
        return True
    return False

def validate_refresh_token(db: Session, token: str) -> Optional[User]:
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    if not refresh_token:
        return None
    return db.query(User).filter(User.id == refresh_token.user_id).first()
