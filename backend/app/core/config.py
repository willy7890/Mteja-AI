from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MTEJA AI"
    SECRET_KEY: str = "super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql+asyncpg://mteja:mteja@localhost:5432/mteja_ai"

    class Config:
        env_file = ".env"

    def model_post_init(self, __context):
        if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with asyncpg")

settings = Settings()
