# teder-sdk

SDK Python oficial do [TEDER](https://teder.com.br) — API de segurança em tempo real para agentes autônomos.

## Instalação

```bash
pip install teder-sdk
```

## Uso em 10 linhas

```python
from teder_sdk import Teder

teder = Teder(api_key="sk-teder-sua-chave-aqui")

result = teder.analyze(
    agent_id="meu-agente-v1",
    agent_goal="responder perguntas sobre produtos da loja",
    user_input=user_message,
)

if result.is_blocked:
    return "Mensagem não permitida."

# Seguro — passe para o agente
response = seu_agente.run(user_message)
```

## Integração com LangChain

```python
from teder_sdk import TederGuard, TederBlockedError

guard = TederGuard(
    api_key="sk-teder-...",
    agent_goal="responder sobre produtos",
)

try:
    guard.check(user_input)
    response = agent.run(user_input)
except TederBlockedError as e:
    response = "Mensagem bloqueada por segurança."
```

## Referência

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `result.action` | `"allow"` \| `"warn"` \| `"block"` | Ação recomendada |
| `result.risk_score` | `float` 0.0–1.0 | Score de risco |
| `result.threats` | `List[str]` | Tipos de ameaça detectados |
| `result.latency_ms` | `float` | Latência da análise |
| `result.is_blocked` | `bool` | Atalho para `action == "block"` |
| `result.is_safe` | `bool` | Atalho para `action == "allow"` |
