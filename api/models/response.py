from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Action(str, Enum):
    allow = "allow"
    warn = "warn"
    block = "block"


class LayerResult(BaseModel):
    triggered: bool
    confidence: float
    threats: List[str]
    latency_ms: float


class AnalyzeResponse(BaseModel):
    request_id: str
    action: Action
    risk_score: float
    threats: List[str]
    session_risk: Optional[float] = None
    layers: dict
    latency_ms: float
    teder_version: str


class HealthResponse(BaseModel):
    status: str
    version: str
    postgres: str
    redis: str


class APIKeyResponse(BaseModel):
    id: str
    key: str
    plan: str
    created_at: str


class APIKeyListItem(BaseModel):
    id: str
    key_prefix: str
    plan: str
    created_at: str
    is_active: bool
