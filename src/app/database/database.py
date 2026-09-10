from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.config import config

engine = create_async_engine(str(config.database_config()), echo=False)
async_session = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session.begin() as session:
        yield session
