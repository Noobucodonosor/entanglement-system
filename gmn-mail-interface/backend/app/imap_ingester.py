"""Background ingester: legge mail dalla casella IMAP e le persiste nel DB."""

import asyncio
import logging
from datetime import datetime

from imap_tools import AND, MailBox

from app.config import get_settings
from app.models import EmailRecord, SessionLocal
from app.score_calculator import calculate_deposit, calculate_score
from app.email_parser import ParsedEmail

logger = logging.getLogger(__name__)


def _process_one(msg, owner_email: str) -> EmailRecord | None:
    parsed = ParsedEmail(
        sender=msg.from_,
        subject=msg.subject or "",
        body=msg.text or msg.html or "",
        received_at=msg.date.isoformat() if msg.date else None,
        attachments=[a.filename for a in msg.attachments if a.filename],
    )
    score = calculate_score(parsed)
    deposit = calculate_deposit(parsed)
    return EmailRecord(
        owner_email=owner_email,
        sender=parsed.sender,
        subject=parsed.subject,
        body=parsed.body,
        received_at=msg.date or datetime.utcnow(),
        score=score,
        deposit=deposit,
        source_uid=str(msg.uid) if msg.uid else None,
    )


def _ingest_once(settings) -> int:
    """Fa una passata: connette, scarica i messaggi nuovi, salva. Ritorna il numero salvato."""
    saved = 0
    with MailBox(settings.imap_host, port=settings.imap_port).login(
        settings.imap_user, settings.imap_password, initial_folder=settings.imap_folder
    ) as mailbox:
        db = SessionLocal()
        try:
            existing_uids = {
                row[0]
                for row in db.query(EmailRecord.source_uid)
                .filter(EmailRecord.owner_email == settings.imap_user)
                .all()
                if row[0]
            }
            for msg in mailbox.fetch(AND(seen=False), mark_seen=False, bulk=True):
                if msg.uid and msg.uid in existing_uids:
                    continue
                record = _process_one(msg, settings.imap_user)
                if record is not None:
                    db.add(record)
                    saved += 1
            db.commit()
        finally:
            db.close()
    return saved


async def run_ingester_loop() -> None:
    """Loop infinito: polling IMAP a intervalli regolari."""
    settings = get_settings()
    if not settings.imap_host or not settings.imap_user or not settings.imap_password:
        logger.info("IMAP non configurato: ingester non avviato.")
        return

    logger.info(
        "IMAP ingester avviato (host=%s, user=%s, poll=%ds)",
        settings.imap_host,
        settings.imap_user,
        settings.imap_poll_seconds,
    )
    while True:
        try:
            count = await asyncio.to_thread(_ingest_once, settings)
            if count:
                logger.info("Ingerite %d nuove email", count)
        except Exception:
            logger.exception("Errore durante l'ingest IMAP")
        await asyncio.sleep(settings.imap_poll_seconds)
