from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


from config import settings


db_url = (
    f"postgresql+asyncpg://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_DB}"
)

_engine = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine

    _engine = create_async_engine(
        db_url,
        echo=settings.DEBUG_ENGINE,
        max_overflow=25,
        pool_size=10,
        pool_timeout=30,
    )
    return _engine


async def _get_async_session() -> AsyncSession:
    async with AsyncSession(get_engine()) as session, session.begin():
        try:
            yield session
        finally:
            await session.close()


async_session = asynccontextmanager(_get_async_session)
