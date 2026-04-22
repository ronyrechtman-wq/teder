"""
Middleware que injeta X-Request-ID em todas as respostas.
Implementado como ASGI puro para não interferir no body da request
(BaseHTTPMiddleware tem bug conhecido que consome o body antes do handler).
"""

import uuid
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = dict(scope.get("headers", [])).get(b"x-request-id", b"").decode() or str(uuid.uuid4())

        async def send_with_header(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_with_header)
