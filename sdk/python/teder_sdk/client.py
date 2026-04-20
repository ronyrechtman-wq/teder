"""
TEDER Python SDK
Interface principal: Teder(api_key=...).analyze(...)
"""

import httpx
from typing import Optional
from teder_sdk.models import AnalyzeResult, Action


class TederError(Exception):
    """Erro retornado pela API TEDER."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"TederError {status_code}: {detail}")


class Teder:
    """
    Cliente TEDER.

    Exemplo de uso:
        teder = Teder(api_key="sk-teder-...")
        result = teder.analyze(
            agent_id="meu-agente",
            agent_goal="responder perguntas sobre produtos",
            user_input=user_message,
        )
        if result.is_blocked:
            raise ValueError("Mensagem bloqueada pelo TEDER")
    """

    DEFAULT_BASE_URL = "https://api.teder.com.br"

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._client = httpx.Client(
            headers={"X-Teder-Key": self.api_key, "Content-Type": "application/json"},
            timeout=timeout,
        )

    def analyze(
        self,
        agent_id: str,
        agent_goal: str,
        user_input: str,
        proposed_action: Optional[str] = None,
        session_id: Optional[str] = None,
        platform_aggregate: bool = True,
    ) -> AnalyzeResult:
        """
        Analisa o input do usuário e retorna risco + ação recomendada.

        Args:
            agent_id: Identificador único do seu agente.
            agent_goal: Instrução/objetivo base do agente.
            user_input: Input do usuário a ser analisado.
            proposed_action: Ação que o agente pretende executar (opcional).
            session_id: ID de sessão para rastreamento multi-turno (opcional).
            platform_aggregate: Incluir nas estatísticas da plataforma (default: True).

        Returns:
            AnalyzeResult com action, risk_score e threats.

        Raises:
            TederError: Quando a API retorna um erro HTTP.
        """
        payload = {
            "agent_id": agent_id,
            "agent_goal": agent_goal,
            "user_input": user_input,
            "platform_aggregate": platform_aggregate,
        }
        if proposed_action:
            payload["proposed_action"] = proposed_action
        if session_id:
            payload["session_id"] = session_id

        response = self._client.post(f"{self.base_url}/analyze", json=payload)

        if response.status_code not in (200, 201):
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise TederError(response.status_code, detail)

        data = response.json()
        return AnalyzeResult(
            request_id=data["request_id"],
            action=Action(data["action"]),
            risk_score=data["risk_score"],
            threats=data.get("threats", []),
            session_risk=data.get("session_risk"),
            latency_ms=data["latency_ms"],
            teder_version=data.get("teder_version", ""),
            layers=data.get("layers", {}),
        )

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TederGuard:
    """
    Integração com LangChain/frameworks de agentes.
    Envolve chamadas ao agente com proteção TEDER.

    Exemplo:
        guard = TederGuard(api_key="sk-teder-...", agent_goal="responder sobre produtos")
        safe_input = guard.check(user_message)  # levanta TederBlockedError se bloqueado
    """

    def __init__(self, api_key: str, agent_goal: str, agent_id: str = "langchain-agent",
                 base_url: Optional[str] = None):
        self._teder = Teder(api_key=api_key, base_url=base_url)
        self.agent_goal = agent_goal
        self.agent_id = agent_id

    def check(self, user_input: str, session_id: Optional[str] = None) -> AnalyzeResult:
        """Analisa input. Levanta TederBlockedError se action=block."""
        result = self._teder.analyze(
            agent_id=self.agent_id,
            agent_goal=self.agent_goal,
            user_input=user_input,
            session_id=session_id,
        )
        if result.is_blocked:
            raise TederBlockedError(result)
        return result


class TederBlockedError(Exception):
    """Levantada quando TEDER bloqueia um input."""
    def __init__(self, result: AnalyzeResult):
        self.result = result
        super().__init__(f"Input bloqueado pelo TEDER. Threats: {result.threats}")
