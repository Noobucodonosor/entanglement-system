"""Endpoint REST dell'API mail interface."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.email_parser import ParsedEmail, parse_raw_email
from app.models import EmailRecord, get_db, init_db
from app.score_calculator import calculate_deposit, calculate_score

router = APIRouter()


@router.on_event("startup")
def on_startup() -> None:
    init_db()


@router.get("/emails")
def list_emails(db: Session = Depends(get_db)):
    records = db.query(EmailRecord).order_by(EmailRecord.received_at.desc()).all()
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
def get_email(email_id: int, db: Session = Depends(get_db)):
    record = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Email non trovata")
    return record


@router.post("/emails/upload")
async def upload_email(file: UploadFile, db: Session = Depends(get_db)):
    raw = await file.read()
    parsed: ParsedEmail = parse_raw_email(raw)
    score = calculate_score(parsed)
    deposit = calculate_deposit(parsed)

    record = EmailRecord(
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
