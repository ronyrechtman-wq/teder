"""
C2 — Classificador PT-BR Próprio
STUB na Wave 1 — retorna confidence: 0.0.
O modelo real será treinado com dados reais no Mês 2.
"""

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class C2Result:
    triggered: bool
    confidence: float
    threats: List[str]
    latency_ms: float


def analyze(text: str) -> C2Result:
    """STUB: retorna confiança zero. Não ativa C3 por conta própria."""
    start = time.perf_counter()
    latency_ms = (time.perf_counter() - start) * 1000
    return C2Result(triggered=False, confidence=0.0, threats=[], latency_ms=latency_ms)
