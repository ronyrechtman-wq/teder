import redis.asyncio as aioredis
from typing import Optional
from api.config import settings

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    """Retorna cliente Redis. Retorna None se indisponível (degraded mode)."""
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis.ping()
        except Exception:
            _redis = None
    return _redis


async def redis_ping() -> bool:
    """Verifica disponibilidade do Redis para /health."""
    try:
        r = await get_redis()
        if r is None:
            return False
        await r.ping()
        return True
    except Exception:
        return False


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
