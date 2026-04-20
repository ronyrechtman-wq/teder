"""
Shield Engine — orquestrador das camadas C1→C2→C3→C4.
"""

import time
import uuid
from typing import Optional

from api.models.request import AnalyzeRequest
from api.models.response import AnalyzeResponse, Action
from api.services import layer1_deterministic, layer2_classifier, layer3_llm, layer4_session
from api.services.scorer import compute_risk_score, compute_action, should_call_c3
from api.config import settings


async def run(request: AnalyzeRequest) -> AnalyzeResponse:
    total_start = time.perf_counter()
    request_id = str(uuid.uuid4())

    combined_text = f"{request.user_input}"
    if request.proposed_action:
        combined_text += f"\n{request.proposed_action}"

    # C1 — Filtro determinístico
    c1 = layer1_deterministic.analyze(combined_text)

    # C2 — Stub (Wave 1)
    c2 = layer2_classifier.analyze(combined_text)

    # C3 — LLM Árbitro (apenas se C1 não tem confiança suficiente)
    c3 = None
    c3_risk_score = 0.0
    c3_confidence = 0.0
    if should_call_c3(c1.confidence):
        c3 = await layer3_llm.analyze(
            agent_goal=request.agent_goal,
            user_input=request.user_input,
            proposed_action=request.proposed_action,
        )
        # Mapeia action do LLM em risk_score
        if c3.raw_response:
            import json
            try:
                data = json.loads(c3.raw_response)
                c3_risk_score = float(data.get("risk_score", 0.1))
                c3_confidence = c3.confidence
            except Exception:
                pass

    # Score final
    risk_score = compute_risk_score(
        c1_triggered=c1.triggered,
        c1_confidence=c1.confidence,
        c3_risk_score=c3_risk_score,
        c3_confidence=c3_confidence,
    )
    action = compute_action(risk_score)

    # Agrega ameaças de todas as camadas
    threats = list(set(c1.threats + (c3.threats if c3 else [])))

    # C4 — Armazenamento de sessão (Wave 1: só guarda, não calcula drift)
    session_risk: Optional[float] = None
    if request.session_id:
        event_data = {
            "request_id": request_id,
            "action": action.value,
            "risk_score": risk_score,
            "threats": threats,
        }
        await layer4_session.store_event(request.session_id, event_data)
        session_risk = await layer4_session.get_session_risk(request.session_id)

    total_latency_ms = (time.perf_counter() - total_start) * 1000

    return AnalyzeResponse(
        request_id=request_id,
        action=action,
        risk_score=round(risk_score, 4),
        threats=threats,
        session_risk=session_risk,
        layers={
            "c1": {"triggered": c1.triggered, "confidence": c1.confidence, "latency_ms": round(c1.latency_ms, 2)},
            "c2": {"triggered": c2.triggered, "confidence": c2.confidence, "latency_ms": round(c2.latency_ms, 2)},
            "c3": {"triggered": c3.triggered, "confidence": c3.confidence, "latency_ms": round(c3.latency_ms, 2)} if c3 else None,
            "c4": {"session_id": request.session_id, "session_risk": session_risk},
        },
        latency_ms=round(total_latency_ms, 2),
        teder_version=settings.TEDER_VERSION,
    )
