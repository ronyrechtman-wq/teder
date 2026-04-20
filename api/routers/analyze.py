from fastapi import APIRouter, Depends
from api.models.request import AnalyzeRequest
from api.models.response import AnalyzeResponse
from api.middleware.auth import get_api_key
from api.middleware.rate_limit import check_rate_limit
from api.services import shield_engine
from api.db.database import AsyncSessionLocal, ShieldEvent, APIKey
import uuid

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, api_key: APIKey = Depends(get_api_key)):
    await check_rate_limit(str(api_key.id), api_key.plan)

    result = await shield_engine.run(request)

    # Persiste evento no Postgres
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
        )
        session.add(event)
        await session.commit()

    return result
