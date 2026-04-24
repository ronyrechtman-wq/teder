import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.middleware.request_id import RequestIDMiddleware
from api.routers import analyze, health, keys, events, sessions
from api.db.database import init_db
from api.config import settings

logger = logging.getLogger("teder")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"TEDER {settings.TEDER_VERSION} iniciando — environment={settings.ENVIRONMENT}")
    try:
        await init_db()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Falha ao inicializar banco de dados: {e} — API sobe sem DB")
    yield
    # Shutdown
    from api.db.redis_client import close_redis
    await close_redis()


app = FastAPI(
    title="TEDER API",
    description="API de segurança em tempo real para agentes autônomos. Detecta e bloqueia prompt injection, data leaks, tool misuse e agent hijacking em < 150ms.",
    version=settings.TEDER_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.teder.com.br", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(health.router)
app.include_router(keys.router)
app.include_router(events.router)
app.include_router(sessions.router)


_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    return FileResponse(os.path.join(_static_dir, "dashboard.html"))


@app.get("/")
async def root():
    return {
        "product": "TEDER",
        "version": settings.TEDER_VERSION,
        "docs": "/docs",
        "health": "/health",
        "dashboard": "/dashboard",
    }
