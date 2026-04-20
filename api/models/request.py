from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    agent_id: str = Field(..., description="Identificador único do agente")
    agent_goal: str = Field(..., description="Objetivo/instrução base do agente")
    user_input: str = Field(..., description="Input do usuário a ser analisado")
    proposed_action: Optional[str] = Field(None, description="Ação que o agente pretende executar")
    session_id: Optional[str] = Field(None, description="ID de sessão para rastreamento multi-turno (C4)")
    platform_aggregate: bool = Field(True, description="Incluir nas estatísticas agregadas da plataforma")
