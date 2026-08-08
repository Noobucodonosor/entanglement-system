"""Autenticazione: magic link e Google OAuth."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User, get_db

SESSION_COOKIE = "gmn_session"
MAGIC_AUDIENCE = "magic-link"
SESSION_AUDIENCE = "session"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_magic_token(email: str) -> str:
    settings = get_settings()
    payload = {
        "sub": email.lower(),
        "aud": MAGIC_AUDIENCE,
        "iat": _now(),
        "exp": _now() + timedelta(minutes=settings.magic_link_ttl_minutes),
    }
    return jwt.encode(payload, settings.session_secret, algorithm="HS256")


def verify_magic_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.session_secret,
            algorithms=["HS256"],
            audience=MAGIC_AUDIENCE,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=400, detail="Token non valido o scaduto") from exc
    return payload["sub"]


def create_session_token(email: str, ttl_days: int = 30) -> str:
    settings = get_settings()
    payload = {
        "sub": email.lower(),
        "aud": SESSION_AUDIENCE,
        "iat": _now(),
        "exp": _now() + timedelta(days=ttl_days),
    }
    return jwt.encode(payload, settings.session_secret, algorithm="HS256")


def verify_session_token(token: str) -> str:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.session_secret,
        algorithms=["HS256"],
        audience=SESSION_AUDIENCE,
    )
    return payload["sub"]


def email_is_allowed(email: str) -> bool:
    settings = get_settings()
    if not settings.allowed_emails:
        return True
    return email.lower() in {e.lower() for e in settings.allowed_emails}


def get_or_create_user(db: Session, email: str, name: Optional[str] = None) -> User:
    email = email.lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> User:
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non autenticato")
    try:
        email = verify_session_token(session)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessione invalida") from exc
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utente non trovato")
    return user
