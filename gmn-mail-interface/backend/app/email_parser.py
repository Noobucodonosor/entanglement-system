"""Parsing email: estrazione di mittente, oggetto, corpo e allegati."""

import email
from email import policy
from email.message import EmailMessage
from typing import Optional

from pydantic import BaseModel


class ParsedEmail(BaseModel):
    sender: str
    subject: str
    body: str
    received_at: Optional[str] = None
    attachments: list[str] = []


def parse_raw_email(raw: bytes) -> ParsedEmail:
    """Esegue il parsing di un'email RFC 5322 grezza."""
    msg: EmailMessage = email.message_from_bytes(raw, policy=policy.default)

    body_part = msg.get_body(preferencelist=("plain", "html"))
    body = body_part.get_content() if body_part else ""

    attachments = [
        part.get_filename()
        for part in msg.iter_attachments()
        if part.get_filename()
    ]

    return ParsedEmail(
        sender=msg.get("From", ""),
        subject=msg.get("Subject", ""),
        body=body,
        received_at=msg.get("Date"),
        attachments=attachments,
    )
