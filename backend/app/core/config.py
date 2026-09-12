from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )

    APP_NAME: str = "MTEJA AI"

    SECRET_KEY: str = "super-secret-key-change-this-in-production"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite+aiosqlite:///./mteja_ai.db"

    # =========================
    # Email
    # =========================
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "Mteja AI"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # =========================
    # Africa's Talking
    # =========================
    AT_USERNAME: str
    AT_API_KEY: str

    # =========================
    # SMS
    # =========================
    SMS_PROVIDER: str = "africastalking"
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_FROM: str = ""

    # =========================
    # Telegram
    # =========================
    TELEGRAM_BOT_TOKEN: str = ""

    # =========================
    # Meta webhooks and APIs
    # =========================
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

    def model_post_init(self, __context):
        allowed_prefixes = (
            "postgresql+asyncpg://",
            "sqlite+aiosqlite://",
            "sqlite://",
        )

        if not self.DATABASE_URL.startswith(allowed_prefixes):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL with asyncpg or "
                "SQLite with aiosqlite"
            )


settings = Settings()