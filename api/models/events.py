from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EventRecord(BaseModel):
    id: str
    request_id: str
    api_key_id: str
    agent_id: str
    action: str
    risk_score: float
    threats: List[str]
    session_id: Optional[str]
    latency_ms: float
    platform_aggregate: bool
    source_ip: Optional[str] = None
    source_country: Optional[str] = None
    created_at: datetime


class EventsResponse(BaseModel):
    items: List[EventRecord]
    total: int
    page: int
    page_size: int
