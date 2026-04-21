from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from datetime import datetime
from api.config import settings


try:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
except Exception as _e:
    import logging
    logging.getLogger("teder").error(f"Falha ao criar engine do banco: {_e}")
    engine = None  # type: ignore
    AsyncSessionLocal = None  # type: ignore


class Base(DeclarativeBase):
    pass


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(128), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)
    plan = Column(String(20), nullable=False, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ShieldEvent(Base):
    __tablename__ = "shield_events"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(36), nullable=False)
    api_key_id = Column(PGUUID(as_uuid=True), nullable=False)
    agent_id = Column(String(255), nullable=False)
    action = Column(String(10), nullable=False)
    risk_score = Column(Float, nullable=False)
    threats = Column(ARRAY(Text), default=[])
    session_id = Column(String(255), nullable=True)
    latency_ms = Column(Float, nullable=False)
    platform_aggregate = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


SCHEMA_SQL = """
-- Tabelas principais
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(128) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    plan VARCHAR(20) NOT NULL DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shield_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(36) NOT NULL,
    api_key_id UUID NOT NULL REFERENCES api_keys(id),
    agent_id VARCHAR(255) NOT NULL,
    action VARCHAR(10) NOT NULL,
    risk_score FLOAT NOT NULL,
    threats TEXT[] DEFAULT '{}',
    session_id VARCHAR(255),
    latency_ms FLOAT NOT NULL,
    platform_aggregate BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shield_events_api_key ON shield_events(api_key_id);
CREATE INDEX IF NOT EXISTS idx_shield_events_created_at ON shield_events(created_at);

-- View materializada para estatísticas da plataforma (dashboard)
CREATE MATERIALIZED VIEW IF NOT EXISTS platform_stats AS
  SELECT
    DATE(created_at) AS day,
    action,
    threats,
    COUNT(*) AS total
  FROM shield_events
  WHERE platform_aggregate = true
  GROUP BY 1, 2, 3;

CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_stats_unique ON platform_stats(day, action, threats);
"""


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Cria tabelas e view materializada se não existirem."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Executa SQL adicional para view e índices
        await conn.execute(__import__("sqlalchemy").text(SCHEMA_SQL))
