from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Action(str, Enum):
    allow = "allow"
    warn = "warn"
    block = "block"


@dataclass
class AnalyzeResult:
    request_id: str
    action: Action
    risk_score: float
    threats: List[str]
    session_risk: Optional[float]
    latency_ms: float
    teder_version: str
    layers: dict = field(default_factory=dict)

    @property
    def is_blocked(self) -> bool:
        return self.action == Action.block

    @property
    def is_safe(self) -> bool:
        return self.action == Action.allow
