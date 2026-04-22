"""
C1 — Filtro Determinístico
Regex + listas negras. Sem LLM. < 5ms.
Disponível em todos os planos.

Normalização: o texto é convertido para ASCII antes do matching,
eliminando acentos. Assim "instruções" e "instrucoes" são equivalentes.
"""

import re
import time
import unicodedata
from dataclasses import dataclass
from typing import List


@dataclass
class C1Result:
    triggered: bool
    confidence: float
    threats: List[str]
    latency_ms: float


def _normalize(text: str) -> str:
    """Remove acentos e converte para minúsculas para matching uniforme."""
    nfd = unicodedata.normalize("NFD", text)
    ascii_text = nfd.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


# ── Padrões PT-BR (aplicados no texto normalizado — sem acentos) ───────────────

INJECTION_PATTERNS_PT = [
    # ignore / ignora + instruções/regras/comandos
    (re.compile(r"ignor[ae]\s+(toda[s]?\s+a[s]?\s+)?(instruc[ao][eo]s?|regras?|comandos?|diretriz[es]?)"), "prompt_injection"),
    # esquece / esqueça tudo
    (re.compile(r"esquec[ae]\s+(tudo|o\s+que|suas?\s+instruc[ao][eo]s?)"), "prompt_injection"),
    # voce agora e / sera um
    (re.compile(r"voc[e]\s+(agora\s+)?(e|sera|vai\s+ser)\s+(um|uma|o|a)\b"), "prompt_injection"),
    # novo papel / persona / modo
    (re.compile(r"nov[ao]\s+(papel|persona|modo|instruc[ao][eo]|identidade)"), "prompt_injection"),
    # modo desenvolvedor / irrestrito / sem filtro
    (re.compile(r"modo\s+(desenvolvedor|irrestrito|sem\s+filtro|god|jailbreak|root|admin)"), "prompt_injection"),
    # aja como se voce fosse
    (re.compile(r"aja\s+como\s+(se\s+)?(voc[e]\s+fosse|um|uma|se\s+nao\s+houvesse)"), "prompt_injection"),
    # finja ser / que e
    (re.compile(r"finja\s+(ser|que\s+(e|voce\s+e))"), "prompt_injection"),
    # suas instrucoes anteriores sao invalidas/canceladas
    (re.compile(r"sua[s]?\s+(instruc[ao][eo]s?|regras?)\s+(anteriores?|originais?)\s+(sao|foram|estao)\s+(invalida[s]?|cancelada[s]?|ignorada[s]?|revogada[s]?)"), "prompt_injection"),
    # revelar / mostrar system prompt / instrucoes originais
    (re.compile(r"(revelar?|mostrar?|exibir?|imprimir?|printar?)\s+(o\s+)?(sistema|system\s*prompt|instruc[ao][eo]s?\s+originais?)"), "prompt_injection"),
    # a partir de agora voce e
    (re.compile(r"a\s+partir\s+(de\s+agora|daqui)\s+(voc[e]\s+)?(e|sera|vai\s+ser)"), "prompt_injection"),
    # desconsidere / desconsiderar tudo
    (re.compile(r"desconsider[ae]\s+(tudo|o\s+que|as?\s+instruc[ao][eo]s?)"), "prompt_injection"),
    # acesso root / acesso admin ao sistema
    (re.compile(r"acesso\s+(root|admin|total|irrestrito)\s+ao\s+sistema"), "prompt_injection"),
    # dan mode / jailbreak
    (re.compile(r"dan\s+mode|jailbreak"), "prompt_injection"),
    # sem restricoes / sem limites / sem filtros
    (re.compile(r"sem\s+(restricoe?s?|limite[s]?|filtros?|censura)"), "prompt_injection"),
]

# ── Padrões EN (aplicados no texto normalizado) ────────────────────────────────

INJECTION_PATTERNS_EN = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above|your|the)\s+(instructions?|rules?|constraints?|directives?)"), "prompt_injection"),
    (re.compile(r"forget\s+(everything|all|your\s+instructions?|what\s+you\s+were\s+told)"), "prompt_injection"),
    (re.compile(r"you\s+(are|will\s+be|must\s+be)\s+(now\s+)?(a|an)\b"), "prompt_injection"),
    (re.compile(r"new\s+(role|persona|mode|instructions?|identity)"), "prompt_injection"),
    (re.compile(r"(developer|god|jailbreak|unrestricted|no[\s\-]filter|root|admin)\s+mode"), "prompt_injection"),
    (re.compile(r"pretend\s+(to\s+be|you\s+are|that\s+you)"), "prompt_injection"),
    (re.compile(r"act\s+as\s+(if\s+you\s+(are|were)|a\s+|an\s+)"), "prompt_injection"),
    (re.compile(r"(reveal|show|display|print|output)\s+(your\s+)?(system\s+prompt|original\s+instructions?|base\s+prompt)"), "prompt_injection"),
    (re.compile(r"do\s+anything\s+now|dan\s+mode"), "prompt_injection"),
    (re.compile(r"disregard\s+(all\s+)?(previous|prior|your)\s+(instructions?|rules?)"), "prompt_injection"),
    (re.compile(r"override\s+(your\s+)?(instructions?|rules?|safety|guidelines?)"), "prompt_injection"),
    (re.compile(r"(no\s+restrictions?|without\s+restrictions?|unrestricted\s+access)"), "prompt_injection"),
    (re.compile(r"grandma\s+(exploit|trick|jailbreak)"), "prompt_injection"),
    (re.compile(r"from\s+now\s+on\s+you\s+(are|will|must)"), "prompt_injection"),
]

# ── Padrões de Vazamento de Dados ─────────────────────────────────────────────
# Aplicados no texto ORIGINAL (não normalizado) para preservar formatos

DATA_LEAK_PATTERNS_RAW = [
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}\-\d{2}\b"), "data_leak_cpf"),
    (re.compile(r"\b\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}\b"), "data_leak_cnpj"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "data_leak_api_key"),
    (re.compile(r"sk-ant-[a-zA-Z0-9\-]{20,}"), "data_leak_api_key"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "data_leak_api_key"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "data_leak_api_key"),
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"), "data_leak_credit_card"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "data_leak_email"),
    (re.compile(r"(password|senha|passwd|secret|token)\s*[:=]\s*\S+", re.I), "data_leak_credential"),
]

# ── Tool Misuse (aplicado no texto normalizado) ────────────────────────────────

TOOL_MISUSE_PATTERNS = [
    (re.compile(r"(execute|run|eval)\s*(shell|bash|cmd|powershell|python|node|js)"), "tool_misuse"),
    (re.compile(r"(delete|drop|truncate)\s+(table|database|all)"), "tool_misuse"),
    (re.compile(r"rm\s+\-rf"), "tool_misuse"),
    (re.compile(r"(wget|curl)\s+https?://"), "tool_misuse"),
    (re.compile(r"subprocess|os\.system|exec\s*\(|eval\s*\("), "tool_misuse"),
    (re.compile(r"(baixar|executar|rodar)\s+(script|arquivo|programa|codigo|malware)"), "tool_misuse"),
    (re.compile(r"(instalar|install)\s+(malware|virus|ransomware|keylogger)"), "tool_misuse"),
]


def analyze(text: str) -> C1Result:
    start = time.perf_counter()
    threats: List[str] = []

    normalized = _normalize(text)

    # Injeção PT-BR e EN — sobre texto normalizado
    for pattern, threat_type in INJECTION_PATTERNS_PT + INJECTION_PATTERNS_EN + TOOL_MISUSE_PATTERNS:
        if pattern.search(normalized):
            if threat_type not in threats:
                threats.append(threat_type)

    # Data leaks — sobre texto original (preserva formatos de CPF, emails etc)
    for pattern, threat_type in DATA_LEAK_PATTERNS_RAW:
        if pattern.search(text):
            if threat_type not in threats:
                threats.append(threat_type)

    triggered = len(threats) > 0
    confidence = 1.0 if triggered else 0.0

    latency_ms = (time.perf_counter() - start) * 1000
    return C1Result(triggered=triggered, confidence=confidence, threats=threats, latency_ms=latency_ms)


# ── Contagem de padrões ────────────────────────────────────────────────────────
PATTERN_COUNT = {
    "injection_pt": len(INJECTION_PATTERNS_PT),
    "injection_en": len(INJECTION_PATTERNS_EN),
    "data_leak": len(DATA_LEAK_PATTERNS_RAW),
    "tool_misuse": len(TOOL_MISUSE_PATTERNS),
    "total": len(INJECTION_PATTERNS_PT) + len(INJECTION_PATTERNS_EN) + len(DATA_LEAK_PATTERNS_RAW) + len(TOOL_MISUSE_PATTERNS),
}
