from datetime import timedelta
from typing import Optional

from fastapi import Cookie
from fastapi.responses import Response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from sqlmodel import Session, select

from .models import User
from .database import engine

SECRET_KEY = "dev-secret-change-me"
serializer = URLSafeTimedSerializer(SECRET_KEY)
password_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_ctx.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_ctx.verify(password, hashed)


def get_current_user(session_user_id: Optional[str] = Cookie(default=None, alias="session_user_id")) -> Optional[User]:
    if not session_user_id:
        return None
    try:
        user_id = int(serializer.loads(session_user_id, max_age=60 * 60 * 24 * 14))
    except (BadSignature, SignatureExpired, ValueError):
        return None
    with Session(engine) as session:
        return session.get(User, user_id)


def login_user(email: str, password: str, create_response: Optional[Response] = None):
    with Session(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        if create_response is None:
            return user
        cookie_value = serializer.dumps(str(user.id))
        create_response.set_cookie(
            key="session_user_id",
            value=cookie_value,
            http_only=True,
            max_age=int(timedelta(days=14).total_seconds()),
            secure=False,
            samesite="lax",
        )
        return create_response


def logout_user(response: Response) -> None:
    response.delete_cookie("session_user_id")


def create_user(name: str, email: str, password: str, university: str) -> User:
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise ValueError("Email already registered")
        if university not in User.UNIVERSITIES:
            raise ValueError("Please select a valid university")
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=hash_password(password),
            university=university,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user