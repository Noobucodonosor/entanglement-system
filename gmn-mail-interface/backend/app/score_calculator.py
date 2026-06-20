"""Calcolo punteggi e acconti a partire da un'email parsata."""

import re
from decimal import Decimal

from app.email_parser import ParsedEmail

AMOUNT_RE = re.compile(r"(\d+[.,]?\d*)\s*(?:€|EUR|euro)", re.IGNORECASE)

KEYWORDS_BONUS = {
    "urgente": 20,
    "priorità": 15,
    "acconto": 10,
    "saldo": 10,
    "fattura": 5,
}


def extract_amounts(text: str) -> list[Decimal]:
    """Estrae importi monetari trovati nel testo."""
    amounts = []
    for match in AMOUNT_RE.findall(text):
        normalized = match.replace(".", "").replace(",", ".")
        try:
            amounts.append(Decimal(normalized))
        except (ValueError, ArithmeticError):
            continue
    return amounts


def calculate_score(parsed: ParsedEmail) -> int:
    """Calcola un punteggio di rilevanza in base a parole chiave."""
    score = 0
    haystack = f"{parsed.subject}\n{parsed.body}".lower()
    for keyword, bonus in KEYWORDS_BONUS.items():
        if keyword in haystack:
            score += bonus
    if parsed.attachments:
        score += 5 * len(parsed.attachments)
    return score


def calculate_deposit(parsed: ParsedEmail, percentage: Decimal = Decimal("0.30")) -> Decimal:
    """Stima l'acconto come percentuale dell'importo principale."""
    amounts = extract_amounts(parsed.body)
    if not amounts:
        return Decimal("0")
    return (max(amounts) * percentage).quantize(Decimal("0.01"))
