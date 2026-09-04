"""Configurazione applicazione, letta da variabili d'ambiente."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    app_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    session_secret: str = Field(default="change-me-in-production", min_length=16)
    database_url: str = "sqlite:///./mail_interface.db"

    # Allowlist degli indirizzi che possono autenticarsi (vuoto = nessuna restrizione)
    allowed_emails: list[str] = Field(default_factory=list)

    # Magic link
    magic_link_ttl_minutes: int = 10

    # SMTP (per invio magic link)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "noreply@example.com"
    smtp_starttls: bool = True

    # Google OAuth (opzionale)
    google_client_id: str | None = None
    google_client_secret: str | None = None

    # IMAP ingester (opzionale)
    imap_host: str | None = None
    imap_port: int = 993
    imap_user: str | None = None
    imap_password: str | None = None
    imap_folder: str = "INBOX"
    imap_poll_seconds: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
