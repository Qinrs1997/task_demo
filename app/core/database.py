from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.models.base import Base

async_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def configure_database(database_url: str | None = None) -> None:
    """Configure async SQLAlchemy engine.

    Tests can call this with a temporary SQLite URL, while normal startup uses
    DATABASE_URL from the environment.
    """
    global async_engine, AsyncSessionLocal

    url = database_url or get_settings().DATABASE_URL
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    async_engine = create_async_engine(url, connect_args=connect_args)
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_engine() -> AsyncEngine:
    if async_engine is None:
        configure_database()
    assert async_engine is not None
    return async_engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if AsyncSessionLocal is None:
        configure_database()
    assert AsyncSessionLocal is not None
    return AsyncSessionLocal


async def init_db() -> None:
    from app.models.task import Task  # noqa: F401

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    from app.models.task import Task  # noqa: F401

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    if async_engine is not None:
        await async_engine.dispose()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
