from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
import hashlib
import hmac
import os
import base64


def _hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return base64.b64encode(salt + key).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        data = base64.b64decode(hashed_password.encode())
        salt = data[:32]
        stored_key = data[32:]
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt, 310000)
        return hmac.compare_digest(key, stored_key)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return _hash_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
