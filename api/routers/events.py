from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from api.db.database import AsyncSessionLocal, ShieldEvent, APIKey
from api.middleware.auth import get_api_key
from api.models.events import EventRecord, EventsResponse
from typing import Optional
import uuid

router = APIRouter()


@router.get("/events", response_model=EventsResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None, description="Filtrar por action: allow, warn, block"),
    api_key: APIKey = Depends(get_api_key),
):
    async with AsyncSessionLocal() as session:
        query = select(ShieldEvent).where(ShieldEvent.api_key_id == api_key.id)

        if action:
            query = query.where(ShieldEvent.action == action)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await session.execute(count_query)).scalar_one()

        # Paginação
        query = query.order_by(ShieldEvent.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        rows = (await session.execute(query)).scalars().all()

    items = [
        EventRecord(
            id=str(row.id),
            request_id=row.request_id,
            api_key_id=str(row.api_key_id),
            agent_id=row.agent_id,
            action=row.action,
            risk_score=row.risk_score,
            threats=row.threats or [],
            session_id=row.session_id,
            latency_ms=row.latency_ms,
            platform_aggregate=row.platform_aggregate,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return EventsResponse(items=items, total=total, page=page, page_size=page_size)
