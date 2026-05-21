import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base  # This imports all models

TEST_DB = 'postgresql+asyncpg://postgres:password123@localhost:5432/sentinelstream_test'


def pytest_configure(config):
    """Create tables before any tests run when PostgreSQL is reachable."""

    async def _create_tables():
        engine = create_async_engine(TEST_DB, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    config._sentinel_test_db_ready = False
    try:
        asyncio.run(_create_tables())
        config._sentinel_test_db_ready = True
    except Exception as exc:
        config._sentinel_test_db_error = repr(exc)


def pytest_collection_modifyitems(config, items):
    if getattr(config, '_sentinel_test_db_ready', False):
        return
    reason = (
        'PostgreSQL test DB unreachable (sentinelstream_test @ localhost). '
        'Start Postgres (e.g. docker compose up -d postgres) or see tests/conftest.py. '
        f"Details: {getattr(config, '_sentinel_test_db_error', 'unknown')}"
    )
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if 'client' in getattr(item, 'fixturenames', ()):
            item.add_marker(skip)


@pytest.fixture
async def client():
    """Each test gets its own engine + session factory."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.api.v1.router import api_router
    from app.api.v1.health import router as health_router
    from app.db.session import get_db

    test_app = FastAPI(title='SentinelStream Test')
    test_app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
                           allow_methods=['*'], allow_headers=['*'])
    test_app.include_router(health_router)
    test_app.include_router(api_router)

    engine = create_async_engine(TEST_DB, echo=False, pool_size=5, max_overflow=0)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url='http://test') as ac:
        yield ac
    test_app.dependency_overrides.clear()
    await engine.dispose()
