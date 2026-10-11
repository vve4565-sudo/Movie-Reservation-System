import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Roles, User
from app.schemas.auth import AuthCreds, HashedCredentials

lg = logging.getLogger(__name__)


@dataclass
class UserRepository:
    session: AsyncSession

    async def create_new_user(
        self,
        credentials: HashedCredentials,
    ) -> User:
        lg.info(
            "create user with data",
            extra=credentials.model_dump(exclude={"password_hash"}),
        )
        user = User(
            nickname=credentials.nickname,
            email=credentials.email,
            password_hash=credentials.password_hash,
            role=Roles.user,
            is_active=True,
            is_superuser=False,
        )
        self.session.add(user)
        await self.session.commit()
        lg.info(
            "success create user with data",
            extra=credentials.model_dump(exclude={"password_hash"}),
        )
        return user

    async def select_user(self, credentials: AuthCreds) -> User | None:
        lg.info(
            "select user with data", extra=credentials.model_dump(exclude={"password"})
        )
        query = select(User).where(
            User.email == credentials.email,
        )
        user = await self.session.execute(query)
        lg.info(
            "success select user with data",
            extra=credentials.model_dump(exclude={"password"}),
        )
        return user.scalar_one_or_none()
