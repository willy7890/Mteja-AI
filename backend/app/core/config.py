from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MTEJA AI"
    SECRET_KEY: str = "super-secret-key-change-this-in-production-123456"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite+aiosqlite:///./mteja_ai.db"

    class Config:
        env_file = ".env"


settings = Settings()