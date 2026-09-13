from dataclasses import dataclass

from database.models import Roles, User
from schemas.auth import AuthCreds, HashedAuthCreds, HashedCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class UserRepository:
    session: AsyncSession

    async def create_new_user(
        self,
        credentials: HashedCredentials,
    ) -> User:
        user = User(
            nickname=credentials.nickname,
            email=credentials.email,
            password_hash=credentials.password_hash,
            Role=Roles.user,
            is_active=True,
            is_superuser=False,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def select_user(self, credentials: AuthCreds) -> User | None:
        query = select(User).where(
            User.email == credentials.email,
        )
        user = await self.session.execute(query)
        return user.scalar()
