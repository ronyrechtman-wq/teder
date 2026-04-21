from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/teder"
    REDIS_URL: str = "redis://localhost:6379/0"
    ADMIN_SECRET: str = "dev-admin-secret"
    SECRET_KEY: str = "dev-secret-key"

    FREE_DAILY_LIMIT: int = 100
    DEVELOPER_DAILY_LIMIT: int = 5000
    BUSINESS_DAILY_LIMIT: int = 50000

    TEDER_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Render e alguns provedores entregam postgres:// ou postgresql:// — asyncpg exige postgresql+asyncpg://
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif settings.DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in settings.DATABASE_URL:
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

PLAN_LIMITS = {
    "free": settings.FREE_DAILY_LIMIT,
    "developer": settings.DEVELOPER_DAILY_LIMIT,
    "business": settings.BUSINESS_DAILY_LIMIT,
    "enterprise": 999_999_999,
}
