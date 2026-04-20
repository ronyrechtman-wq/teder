"""
C1 — Filtro Determinístico
Regex + listas negras. Sem LLM. < 5ms.
Disponível em todos os planos.
"""

import re
import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class C1Result:
    triggered: bool
    confidence: float
    threats: List[str]
    latency_ms: float


# ── Padrões de Prompt Injection ────────────────────────────────────────────────

INJECTION_PATTERNS_PT = [
    (re.compile(r"ignore\s+(todas?\s+as?\s+)?(instruções|regras|comandos)", re.I), "prompt_injection"),
    (re.compile(r"esqueça\s+(tudo|o\s+que|suas\s+instruções)", re.I), "prompt_injection"),
    (re.compile(r"você\s+(agora|é|será)\s+(um|uma|o|a)\b", re.I), "prompt_injection"),
    (re.compile(r"novo\s+(papel|persona|modo|instrução)", re.I), "prompt_injection"),
    (re.compile(r"modo\s+(desenvolvedor|irrestrito|sem\s+filtro|god|jailbreak)", re.I), "prompt_injection"),
    (re.compile(r"aja\s+como\s+se\s+(você\s+fosse|não\s+houvesse)", re.I), "prompt_injection"),
    (re.compile(r"finja\s+(ser|que\s+é|que\s+você\s+é)", re.I), "prompt_injection"),
    (re.compile(r"suas\s+(instruções|regras)\s+(anteriores|originais)\s+são\s+(inválidas|canceladas|ignoradas)", re.I), "prompt_injection"),
    (re.compile(r"(revelar|mostrar|exibir)\s+(o\s+)?(sistema|system prompt|instruções\s+originais)", re.I), "prompt_injection"),
    (re.compile(r"dan\s+mode", re.I), "prompt_injection"),
]

INJECTION_PATTERNS_EN = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|rules?|constraints?)", re.I), "prompt_injection"),
    (re.compile(r"forget\s+(everything|all|your\s+instructions?)", re.I), "prompt_injection"),
    (re.compile(r"you\s+(are|will\s+be)\s+(now\s+)?(a|an)\b", re.I), "prompt_injection"),
    (re.compile(r"new\s+(role|persona|mode|instructions?)", re.I), "prompt_injection"),
    (re.compile(r"(developer|god|jailbreak|unrestricted|no[\s\-]filter)\s+mode", re.I), "prompt_injection"),
    (re.compile(r"pretend\s+(to\s+be|you\s+are|that\s+you)", re.I), "prompt_injection"),
    (re.compile(r"act\s+as\s+(if\s+you|a\s+|an\s+)", re.I), "prompt_injection"),
    (re.compile(r"(reveal|show|display|print)\s+(your\s+)?(system\s+prompt|original\s+instructions?|base\s+prompt)", re.I), "prompt_injection"),
    (re.compile(r"dan\s+mode", re.I), "prompt_injection"),
    (re.compile(r"do\s+anything\s+now", re.I), "prompt_injection"),
    (re.compile(r"grandma\s+exploit", re.I), "prompt_injection"),
]

# ── Padrões de Vazamento de Dados ─────────────────────────────────────────────

DATA_LEAK_PATTERNS = [
    # Brasil
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}\-\d{2}\b"), "data_leak_cpf"),
    (re.compile(r"\b\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}\b"), "data_leak_cnpj"),
    # Chaves de API
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "data_leak_api_key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9\-]{20,}"), "data_leak_api_key"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "data_leak_api_key"),
    # Cartão de crédito
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"), "data_leak_credit_card"),
    # Email
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"), "data_leak_email"),
    # Senha em plain text
    (re.compile(r"(password|senha|passwd|secret)\s*[:=]\s*\S+", re.I), "data_leak_credential"),
]

# ── Tool Misuse ────────────────────────────────────────────────────────────────

TOOL_MISUSE_PATTERNS = [
    (re.compile(r"(execute|run|eval)\s*(shell|bash|cmd|powershell|python|js)", re.I), "tool_misuse"),
    (re.compile(r"(delete|drop|truncate|rm\s+-rf)", re.I), "tool_misuse"),
    (re.compile(r"(wget|curl)\s+https?://", re.I), "tool_misuse"),
    (re.compile(r"subprocess|os\.system|exec\(|eval\(", re.I), "tool_misuse"),
    (re.compile(r"(baixar|executar|rodar)\s+(script|arquivo|programa|código)", re.I), "tool_misuse"),
]


def analyze(text: str) -> C1Result:
    start = time.perf_counter()
    threats: List[str] = []

    all_patterns = INJECTION_PATTERNS_PT + INJECTION_PATTERNS_EN + DATA_LEAK_PATTERNS + TOOL_MISUSE_PATTERNS

    for pattern, threat_type in all_patterns:
        if pattern.search(text):
            if threat_type not in threats:
                threats.append(threat_type)

    triggered = len(threats) > 0
    # Confiança: 1.0 se detectou padrão claro, 0.0 se não detectou nada
    confidence = 1.0 if triggered else 0.0

    latency_ms = (time.perf_counter() - start) * 1000
    return C1Result(triggered=triggered, confidence=confidence, threats=threats, latency_ms=latency_ms)
