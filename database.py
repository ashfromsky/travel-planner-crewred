from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from config import settings

import models.models  # noqa: F401

engine = create_async_engine(settings.DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


import os

async def init_db() -> None:
    if settings.DATABASE_URL.startswith("sqlite"):
        db_path = settings.DATABASE_URL.split(":///")[1] if ":///" in settings.DATABASE_URL else None
        if db_path and db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
