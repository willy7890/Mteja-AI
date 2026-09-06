from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

   
    APP_NAME: str = "MTEJA AI"
    SECRET_KEY: str = "super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite+aiosqlite:///./mteja_ai.db"

  
    TELEGRAM_BOT_TOKEN: str | None = None

    
    EMAIL_PROVIDER: str = "resend"              
    EMAIL_API_KEY: str | None = None
    EMAIL_FROM: str = "noreply@yourdomain.com"
    EMAIL_FROM_NAME: str = "Mteja AI"

   
    SMS_PROVIDER: str = "twilio"                
    SMS_API_KEY: str | None = None
    SMS_API_SECRET: str | None = None
    SMS_FROM: str | None = None


    def model_post_init(self, __context):
        allowed_prefixes = (
            "postgresql+asyncpg://",
            "sqlite+aiosqlite://",
            "sqlite://",
        )
        if not self.DATABASE_URL.startswith(allowed_prefixes):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL with asyncpg or SQLite with aiosqlite"
            )


settings = Settings()