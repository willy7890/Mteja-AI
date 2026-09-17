from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "MTEJA AI API"
    APP_NAME: str = "MTEJA AI API"

    # Base Database URL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:2589Mteja@localhost:5432/mteja_ai_db"

    # Mail / SMTP Configuration
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = "noreply@mteja.ai"
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Mteja AI"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # Africa's Talking SMS Credentials
    AT_USERNAME: Optional[str] = "sandbox"
    AT_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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


settings = Settings()