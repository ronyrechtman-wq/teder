import asyncio
import uuid
import logging

import httpx
from fastapi import APIRouter, Depends, Request
from api.models.request import AnalyzeRequest
from api.models.response import AnalyzeResponse
from api.middleware.auth import get_api_key
from api.middleware.rate_limit import check_rate_limit
from api.services import shield_engine
from api.db.database import AsyncSessionLocal, ShieldEvent, APIKey

logger = logging.getLogger("teder")
router = APIRouter()

# Cache em memória: ip → "🇧🇷 Brazil"
_geo_cache: dict[str, str] = {}


def _extract_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


async def _resolve_country(ip: str) -> str | None:
    """Lookup de geolocalização server-side via ipwho.is. Retorna 'Flag Country' ou None."""
    if not ip or ip in ("127.0.0.1", "::1"):
        return None
    if ip in _geo_cache:
        return _geo_cache[ip]
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"https://ipwho.is/{ip}")
            d = r.json()
            if d.get("success"):
                cc = (d.get("country_code") or "").upper()
                flag = d.get("flag", {}).get("emoji", "")
                country = d.get("country", ip)
                result = f"{flag} {country}".strip() if flag else country
                _geo_cache[ip] = result
                return result
    except Exception as e:
        logger.debug(f"Geo lookup falhou para {ip}: {e}")
    return None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: Request, request: AnalyzeRequest, api_key: APIKey = Depends(get_api_key)):
    await check_rate_limit(str(api_key.id), api_key.plan)

    source_ip = _extract_ip(req)
    result = await shield_engine.run(request)

    # Persiste evento no Postgres (fire-and-forget para não atrasar a resposta)
    async def _save():
        try:
            country = await _resolve_country(source_ip) if source_ip else None
            async with AsyncSessionLocal() as session:
                event = ShieldEvent(
                    id=uuid.uuid4(),
                    request_id=result.request_id,
                    api_key_id=api_key.id,
                    agent_id=request.agent_id,
                    action=result.action.value,
                    risk_score=result.risk_score,
                    threats=result.threats,
                    session_id=request.session_id,
                    latency_ms=result.latency_ms,
                    platform_aggregate=request.platform_aggregate,
                    source_ip=source_ip,
                    source_country=country,
                )
                session.add(event)
                await session.commit()
        except Exception as e:
            logger.error(f"Falha ao persistir evento: {e}")

    asyncio.ensure_future(_save())

    return result
