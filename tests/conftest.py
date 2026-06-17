import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from main import app
from database import get_session
from services.aic_service import aic_service

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def mock_aic_service():
    original_get_artwork = aic_service.get_artwork

    async def mock_get_artwork(external_id: int | str) -> dict | None:
        try:
            ext_id = int(external_id)
        except (ValueError, TypeError):
            return None
        if ext_id == 999999:
            return None
        return {"id": ext_id, "title": f"Mock Artwork {ext_id}"}

    aic_service.get_artwork = AsyncMock(side_effect=mock_get_artwork)
    yield aic_service.get_artwork
    aic_service.get_artwork = original_get_artwork
