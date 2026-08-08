"""Invio email transazionali (magic link)."""

import logging
from email.message import EmailMessage

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> None:
    """Invia un'email tramite SMTP, oppure logga su stdout se SMTP non configurato."""
    settings = get_settings()

    if not settings.smtp_host or not settings.smtp_user:
        logger.warning(
            "SMTP non configurato. Email NON inviata. Destinatario: %s\n"
            "Oggetto: %s\n--- CORPO ---\n%s\n--- FINE ---",
            to,
            subject,
            body,
        )
        return

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=settings.smtp_starttls,
    )
