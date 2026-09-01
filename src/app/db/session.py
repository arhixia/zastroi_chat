from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    """FastAPI-зависимость: асинхронная сессия БД на время запроса."""
    async with AsyncSessionLocal() as session:
        yield session