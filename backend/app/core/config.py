from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database Configuration (Inahitajika ili kusoma DATABASE_URL kutoka .env/Render)
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # General App Settings
    PROJECT_NAME: str = "MTEJA AI API"
    APP_NAME: str = "Mteja AI"
    DATABASE_URL: str = "sqlite+aiosqlite:///./mteja.db"  # badilisha kwenye .env kwa database halisi
    FRONTEND_URL: str = "http://localhost:5173"
    SECRET_KEY: str = "super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_OTP_SEND: int = 5
    RATE_LIMIT_OTP_VERIFY: int = 10
    RATE_LIMIT_LOGIN: int = 10
    RATE_LIMIT_REGISTER: int = 5
    RATE_LIMIT_AI_GENERATE: int = 30
    RATE_LIMIT_MESSAGE_SEND: int = 60
    RATE_LIMIT_ORG_CEILING: int = 300

    # OpenAI & AI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    VOICE_TRANSCRIPTION_MODEL: str = "whisper-1"
    VOICE_TTS_MODEL: str = "gpt-4o-mini-tts"
    VOICE_TTS_VOICE: str = "alloy"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Mail / SMTP Configuration
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = "noreply@mteja.ai"
    MAIL_FROM_NAME: str = "Mteja AI"
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # Africa's Talking & SMS Credentials
    AT_USERNAME: Optional[str] = "sandbox"
    AT_API_KEY: Optional[str] = None
    SMS_PROVIDER: str = "africastalking"
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_FROM: str = ""

    # Telegram Integration
    TELEGRAM_BOT_TOKEN: str = ""

    # Meta / Facebook / WhatsApp / Instagram Webhooks
    META_APP_SECRET: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    FACEBOOK_VERIFY_TOKEN: str = ""
    FACEBOOK_ACCESS_TOKEN: str = ""
    FACEBOOK_PAGE_ID: str = ""
    INSTAGRAM_VERIFY_TOKEN: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_PAGE_ID: str = ""

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Ensures async connection string uses an async driver (e.g. asyncpg)."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Derives a synchronous connection string for sync scripts/tools."""
        url = self.DATABASE_URL
        if "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        elif "sqlite+aiosqlite://" in url:
            return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return url

    def model_post_init(self, __context):
        allowed_prefixes = (
            "postgresql+asyncpg://",
            "postgresql://",
            "sqlite+aiosqlite://",
            "sqlite://",
        )

        if not self.DATABASE_URL.startswith(allowed_prefixes):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL with asyncpg or "
                "SQLite with aiosqlite"
            )


settings = Settings()
