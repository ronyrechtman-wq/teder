import os
import pytest

# Define variáveis mínimas para testes sem banco real
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/teder_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("ADMIN_SECRET", "test-admin-secret")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
