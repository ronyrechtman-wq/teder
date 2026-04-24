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
    source_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


import logging
from sqlalchemy import text

_log = logging.getLogger("teder")

# Índices simples — sem arrays (btree não suporta TEXT[])
INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_shield_events_api_key ON shield_events(api_key_id);
CREATE INDEX IF NOT EXISTS idx_shield_events_created_at ON shield_events(created_at);
"""

# View materializada sem índice único em coluna array
MATVIEW_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS platform_stats AS
  SELECT
    DATE(created_at) AS day,
    action,
    COUNT(*) AS total
  FROM shield_events
  WHERE platform_aggregate = true
  GROUP BY 1, 2;
"""

MATVIEW_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_stats_unique
  ON platform_stats(day, action);
"""


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Cria tabelas, índices e view materializada separadamente para isolar falhas."""
    # 1. Tabelas ORM — transação própria
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _log.info("Tabelas criadas/verificadas")

    # 2. Migrações aditivas — ignora se a coluna já existir
    try:
        async with engine.begin() as conn:
            await conn.execute(text(
                "ALTER TABLE shield_events ADD COLUMN IF NOT EXISTS source_ip VARCHAR(45)"
            ))
    except Exception as e:
        _log.warning(f"Migração source_ip: {e}")

    # 3. Índices — ignora se já existirem ou falharem
    try:
        async with engine.begin() as conn:
            await conn.execute(text(INDEXES_SQL))
    except Exception as e:
        _log.warning(f"Índices: {e}")

    # 3. View materializada — ignora se já existir
    try:
        async with engine.begin() as conn:
            await conn.execute(text(MATVIEW_SQL))
        async with engine.begin() as conn:
            await conn.execute(text(MATVIEW_INDEX_SQL))
    except Exception as e:
        _log.warning(f"Materialized view: {e}")
