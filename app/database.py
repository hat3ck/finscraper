from typing import AsyncIterator, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.settings.settings import get_settings

settings = get_settings()
Base = declarative_base()


class DatabaseSessionManager:
    """
    Manages creation of async SQLAlchemy engine and sessions.
    Safe for both FastAPI and pytest-asyncio usage.
    """

    def __init__(self, database_url: str, engine_kwargs: dict[str, Any] | None = None):
        self._database_url = database_url
        self._engine_kwargs = engine_kwargs or {}
        self._engine = None
        self._sessionmaker = None

    def init_engine(self):
        """(Re)initialize engine and sessionmaker for current event loop."""
        if self._engine is None:
            self._engine = create_async_engine(self._database_url, **self._engine_kwargs)
            self._sessionmaker = async_sessionmaker(
                self._engine, expire_on_commit=False, autoflush=False, autocommit=False
            )

    def get_engine(self):
        if self._engine is None:
            self.init_engine()
        return self._engine

    async def close(self):
        """Dispose of the engine when shutting down."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Provide a one-off async connection."""
        self.init_engine()
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide a session bound to the current loop."""
        self.init_engine()
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def reset(self):
        """Dispose engine and reset sessionmaker. Safe for pytest loop resets."""
        if self._engine is not None:
            await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None


# Create manager — note: engine is initialized lazily (loop-safe)
sessionmanager = DatabaseSessionManager(
    settings.database_url,
    {"echo": settings.echo_sql, "future": True}
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency for FastAPI routes or tests.
    Ensures a session tied to the current event loop.
    """
    async with sessionmanager.session() as session:
        yield session
