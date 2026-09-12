from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Mteja AI"
    DATABASE_URL: str = "postgresql+asyncpg://Mteja_Ai_user:2589Mteja@localhost:5432/mteja_ai_db"

    # Mail Settings
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@mteja.ai"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    AT_USERNAME: str = "sandbox"  
    AT_API_KEY: str = "your_api_key_here"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()