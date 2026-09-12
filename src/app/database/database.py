from collections.abc import AsyncGenerator

from config.config import config
from config.security import hash_password
from database.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(str(config.database_config), echo=False)
async_session_factory = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False
)


async def get_session():
    async with async_session_factory() as session:
        yield session


async def init_db():
    async with async_session_factory() as session:
        query = select(User).where(
            User.nickname == config.SUPERUSER_NAME,
            User.email == config.SUPERUSER_EMAIL,
        )
        user = await session.scalar(query)

        if not user:
            new_user = User(
                nickname=config.SUPERUSER_NAME,
                email=config.SUPERUSER_EMAIL,
                password_hash=await hash_password(
                    config.SUPERUSER_PASSWORD,
                ),
                is_active=True,
                is_superuser=True,
            )

            session.add(new_user)
            await session.commit()
