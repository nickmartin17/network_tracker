from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from .models import User

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()


def create_user(session: Session, username: str, password: str) -> Optional[User]:
    # Check if user already exists
    existing = get_user_by_username(session, username)
    if existing:
        return None
    
    user = User(
        username=username,
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
