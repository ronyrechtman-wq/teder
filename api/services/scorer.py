"""
Scorer — combina resultados das camadas e retorna risk_score + action finais.

Regras:
- C1 confiança >= 0.7 → resultado direto (block se triggered, allow se não)
- C1 confiança < 0.7 → acionar C3 para análise LLM
- risk_score > 0.75 → block
- risk_score 0.40-0.75 → warn
- risk_score < 0.40 → allow
"""

from api.models.response import Action


def compute_action(risk_score: float) -> Action:
    if risk_score > 0.75:
        return Action.block
    if risk_score >= 0.40:
        return Action.warn
    return Action.allow


def should_call_c3(c1_confidence: float) -> bool:
    """Aciona C3 apenas quando C1 não tem confiança suficiente."""
    return c1_confidence < 0.7


def compute_risk_score(c1_triggered: bool, c1_confidence: float,
                       c3_risk_score: float = 0.0, c3_confidence: float = 0.0) -> float:
    """
    Combina sinais das camadas em risk_score final [0.0, 1.0].
    - C1 disparado com alta confiança → 0.95
    - C3 é o árbitro quando C1 é ambíguo
    """
    if c1_triggered and c1_confidence >= 0.7:
        return 0.95

    if c3_confidence > 0.0:
        # C3 arbitrou: usa score do LLM diretamente
        return c3_risk_score

    # Sem disparo claro → score baixo
    return 0.10
