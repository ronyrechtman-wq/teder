"""
Middleware de autenticação via X-Teder-Key.
Hash SHA-256 da key é armazenado no Postgres.
"""

import hashlib
from fastapi import Request, HTTPException
from sqlalchemy import select
from api.db.database import AsyncSessionLocal, APIKey


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def get_api_key(request: Request) -> APIKey:
    """Valida X-Teder-Key e retorna o objeto APIKey do banco."""
    raw_key = request.headers.get("X-Teder-Key")
    if not raw_key:
        raise HTTPException(status_code=401, detail="X-Teder-Key header ausente")

    key_hash = hash_key(raw_key)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
        )
        api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=401, detail="API key inválida ou revogada")

    return api_key
