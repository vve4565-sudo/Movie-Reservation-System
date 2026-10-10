import asyncio
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

os.environ.update({
    "DATABASE_SCHEME": "postgresql+asyncpg",
    "DATABASE_HOST": "127.0.0.1",
    "DATABASE_PORT": "5432",
    "DATABASE_USER": "test",
    "DATABASE_PASSWORD": "test",
    "DATABASE_PATH": "movie_test",
    "SUPERUSER_NAME": "test-admin",
    "SUPERUSER_EMAIL": "test-admin@example.test",
    "SUPERUSER_PASSWORD": "test-password",
    "JWT_SECRET_KEY": "test-only-secret",
    "REDIS_PORT": "6379",
})


class MemoryRedis:
    async def get(self, key: str) -> None:
        return None

    async def set(self, key: str, value: str, *args, **kwargs) -> bool:
        return True

    async def delete(self, *keys: str) -> int:
        return 0


@pytest.fixture
def test_session_factory(tmp_path: Path) -> Iterator[async_sessionmaker[AsyncSession]]:
    from app.database.models import Base

    database_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path}",
        poolclass=NullPool,
    )

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    yield async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(engine.dispose())


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> Iterator[TestClient]:
    import app.config.redis as redis_config
    from app import main
    from app.database.database import get_session
    from app.service.rate_limiter import RateLimiter

    async def skip_database_initialization() -> None:
        return None

    async def skip_rate_limit(self, request, call_next):
        return await call_next(request)

    async def test_session():
        async with test_session_factory() as session:
            yield session

    monkeypatch.setattr(main, "init_db", skip_database_initialization)
    monkeypatch.setattr(RateLimiter, "dispatch", skip_rate_limit)
    monkeypatch.setattr(redis_config, "cache_movie_redis", MemoryRedis())
    main.app.dependency_overrides[get_session] = test_session

    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.clear()
