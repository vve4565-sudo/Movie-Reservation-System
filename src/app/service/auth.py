from dataclasses import dataclass

from config.security import dummy_hash, hash_password, verify_password
from database.models import User
from repository.user import UserRepository
from schemas.auth import AuthCreds, FullCredentials, HashedAuthCreds, HashedCredentials
from sqlalchemy.exc import IntegrityError


@dataclass
class AuthService:
    UserRepository: UserRepository

    async def register_user(self, credentials: FullCredentials) -> User | None:
        hashed_password = await hash_password(credentials.password)
        new_credentials = HashedCredentials(
            **credentials.model_dump(exclude={"password"}),
            password_hash=hashed_password,
        )

        try:
            user = await self.UserRepository.create_new_user(new_credentials)
            return user
        except IntegrityError:
            return None

    async def authenticate_user(self, credentials: AuthCreds) -> User | None:
        user = await self.UserRepository.select_user(credentials)

        if not user:
            await verify_password(credentials.password, dummy_hash)
            return None
            # raise Exception("Нет пользователя")

        elif not await verify_password(credentials.password, user.password_hash):
            return None
            # raise Exception("неверный пароль")

        return user
