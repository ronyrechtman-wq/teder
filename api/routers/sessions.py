"""
Rotas de sessão — Wave 1: placeholder para Wave 2 (C4 drift logic).
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Wave 2: retornará histórico e session_risk calculado."""
    return {"session_id": session_id, "session_risk": None, "note": "C4 drift logic disponível na Wave 2"}
