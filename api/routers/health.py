from fastapi import APIRouter
from api.models.response import HealthResponse
from api.db.redis_client import redis_ping
from api.db.database import engine
from api.config import settings
from sqlalchemy import text

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    # Postgres
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        postgres_status = "ok"
    except Exception as e:
        postgres_status = f"error: {e}"

    # Redis
    redis_ok = await redis_ping()
    redis_status = "ok" if redis_ok else "unavailable"

    overall = "ok" if postgres_status == "ok" else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.TEDER_VERSION,
        postgres=postgres_status,
        redis=redis_status,
    )
