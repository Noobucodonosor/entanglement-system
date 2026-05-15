"""Endpoint REST: auth (magic link + Google OAuth) e gestione email."""

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import (
    SESSION_COOKIE,
    create_magic_token,
    create_session_token,
    email_is_allowed,
    get_current_user,
    get_or_create_user,
    verify_magic_token,
)
from app.config import get_settings
from app.email_parser import ParsedEmail, parse_raw_email
from app.mailer import send_email
from app.models import EmailRecord, User, get_db
from app.score_calculator import calculate_deposit, calculate_score

router = APIRouter()

settings = get_settings()
oauth = OAuth()
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


# ---------- Auth: magic link ----------


class MagicRequest(BaseModel):
    email: EmailStr


@router.post("/auth/request")
async def auth_request(payload: MagicRequest):
    email = payload.email.lower()
    if not email_is_allowed(email):
        # Risposta volutamente generica per non rivelare l'allowlist
        return {"ok": True}

    token = create_magic_token(email)
    link = f"{settings.app_url}/api/auth/verify?token={token}"
    body = (
        "Ciao,\n\n"
        f"clicca qui per accedere a GMN Mail Interface (link valido {settings.magic_link_ttl_minutes} minuti):\n\n"
        f"{link}\n\n"
        "Se non hai richiesto tu questo accesso, ignora il messaggio."
    )
    await send_email(email, "Il tuo link di accesso", body)
    return {"ok": True}


@router.get("/auth/verify")
def auth_verify(token: str, db: Session = Depends(get_db)):
    email = verify_magic_token(token)
    if not email_is_allowed(email):
        raise HTTPException(status_code=403, detail="Email non autorizzata")
    get_or_create_user(db, email)
    session_token = create_session_token(email)

    response = RedirectResponse(url=settings.frontend_url, status_code=302)
    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        httponly=True,
        secure=settings.app_url.startswith("https"),
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.post("/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}


@router.get("/auth/me")
def auth_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}


# ---------- Auth: Google OAuth ----------


@router.get("/auth/google/login")
async def google_login(request: Request):
    if "google" not in oauth._clients:
        raise HTTPException(status_code=503, detail="Google OAuth non configurato")
    redirect_uri = f"{settings.app_url}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    if "google" not in oauth._clients:
        raise HTTPException(status_code=503, detail="Google OAuth non configurato")
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    userinfo = token.get("userinfo") or await oauth.google.userinfo(token=token)
    email = (userinfo.get("email") or "").lower()
    name = userinfo.get("name")
    if not email:
        raise HTTPException(status_code=400, detail="Email non ricevuta da Google")
    if not email_is_allowed(email):
        raise HTTPException(status_code=403, detail="Email non autorizzata")

    get_or_create_user(db, email, name=name)
    session_token = create_session_token(email)
    response = RedirectResponse(url=settings.frontend_url, status_code=302)
    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        httponly=True,
        secure=settings.app_url.startswith("https"),
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response


# ---------- Email API (protette) ----------


@router.get("/emails")
def list_emails(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    records = (
        db.query(EmailRecord)
        .filter(
            (EmailRecord.owner_email == user.email) | (EmailRecord.owner_email.is_(None))
        )
        .order_by(EmailRecord.received_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "sender": r.sender,
            "subject": r.subject,
            "score": r.score,
            "deposit": float(r.deposit or 0),
            "received_at": r.received_at.isoformat() if r.received_at else None,
        }
        for r in records
    ]


@router.get("/emails/{email_id}")
def get_email(
    email_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = (
        db.query(EmailRecord)
        .filter(EmailRecord.id == email_id)
        .filter(
            (EmailRecord.owner_email == user.email) | (EmailRecord.owner_email.is_(None))
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Email non trovata")
    return {
        "id": record.id,
        "sender": record.sender,
        "subject": record.subject,
        "body": record.body,
        "score": record.score,
        "deposit": float(record.deposit or 0),
        "received_at": record.received_at.isoformat() if record.received_at else None,
    }


@router.post("/emails/upload")
async def upload_email(
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    raw = await file.read()
    parsed: ParsedEmail = parse_raw_email(raw)
    score = calculate_score(parsed)
    deposit = calculate_deposit(parsed)

    record = EmailRecord(
        owner_email=user.email,
        sender=parsed.sender,
        subject=parsed.subject,
        body=parsed.body,
        score=score,
        deposit=deposit,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "score": score, "deposit": float(deposit)}
