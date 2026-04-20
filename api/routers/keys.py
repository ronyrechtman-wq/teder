import uuid
import secrets
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import select
from api.db.database import AsyncSessionLocal, APIKey
from api.middleware.auth import hash_key
from api.models.response import APIKeyResponse, APIKeyListItem
from api.config import settings
from typing import List

router = APIRouter()


def require_admin(x_admin_secret: str = Header(..., alias="X-Admin-Secret")):
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin secret inválido")


@router.post("/keys", response_model=APIKeyResponse, dependencies=[Depends(require_admin)])
async def create_key(plan: str = "free"):
    if plan not in ("free", "developer", "business", "enterprise"):
        raise HTTPException(status_code=400, detail=f"Plano inválido: {plan}")

    raw_key = f"sk-teder-{secrets.token_urlsafe(32)}"
    key_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        api_key = APIKey(
            id=key_id,
            key_hash=hash_key(raw_key),
            key_prefix=raw_key[:20],
            plan=plan,
        )
        session.add(api_key)
        await session.commit()

    return APIKeyResponse(
        id=str(key_id),
        key=raw_key,
        plan=plan,
        created_at=api_key.created_at.isoformat(),
    )


@router.delete("/keys/{key_id}", dependencies=[Depends(require_admin)])
async def revoke_key(key_id: str):
    try:
        key_uuid = uuid.UUID(key_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(APIKey).where(APIKey.id == key_uuid))
        api_key = result.scalar_one_or_none()
        if not api_key:
            raise HTTPException(status_code=404, detail="Key não encontrada")
        api_key.is_active = False
        await session.commit()

    return {"message": "Key revogada com sucesso", "id": key_id}
