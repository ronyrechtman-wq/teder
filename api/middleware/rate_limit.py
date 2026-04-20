"""
Rate limiting por API key, por dia.
Usa Redis como contador. Fallback: permite requisição se Redis indisponível.
"""

from datetime import date
from fastapi import HTTPException
from api.db.redis_client import get_redis
from api.config import PLAN_LIMITS


async def check_rate_limit(api_key_id: str, plan: str) -> None:
    """Levanta 429 se a key ultrapassou o limite diário."""
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    today = date.today().isoformat()
    redis_key = f"teder:rl:{api_key_id}:{today}"

    r = await get_redis()
    if r is None:
        # Redis indisponível — opera sem rate limit (degraded)
        return

    try:
        count = await r.incr(redis_key)
        if count == 1:
            # Primeira requisição do dia — TTL de 25 horas para cobrir fusos
            await r.expire(redis_key, 90000)

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Limite diário de {limit} requisições atingido para o plano {plan}",
                headers={"Retry-After": "86400"},
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Falha silenciosa — não derrubar /analyze
