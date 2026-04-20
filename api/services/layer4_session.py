"""
C4 — Rastreamento de Sessão Multi-turno
Wave 1: apenas armazenamento no Redis. session_risk retorna None.
A lógica de drift será implementada na Wave 2.
"""

import json
import time
from typing import Optional

from api.db.redis_client import get_redis


SESSION_TTL = 3600  # 1 hora


async def store_event(session_id: str, event: dict) -> None:
    """Armazena evento da sessão no Redis."""
    r = await get_redis()
    if r is None:
        return  # Redis indisponível — opera sem C4

    key = f"teder:session:{session_id}"
    try:
        existing = await r.get(key)
        events = json.loads(existing) if existing else []
        events.append(event)
        # Mantém apenas os últimos 50 eventos por sessão
        events = events[-50:]
        await r.setex(key, SESSION_TTL, json.dumps(events))
    except Exception:
        pass  # Falha silenciosa — não derrubar /analyze


async def get_session_risk(session_id: str) -> Optional[float]:
    """
    Wave 1: retorna None.
    Wave 2: calculará drift de intenção baseado no histórico.
    """
    return None
