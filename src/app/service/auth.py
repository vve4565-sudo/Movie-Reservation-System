import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.config.security import dummy_hash, hash_password, verify_password
from app.database.models import User
from app.exceptions.auth import UserAlreadyExists, UserNotExists, WrongPassword
from app.repository.user import UserRepository
from app.schemas.auth import (
    AuthCreds,
    FullCredentials,
    HashedCredentials,
)

lg = logging.getLogger(__name__)


@dataclass
class AuthService:
    UserRepository: UserRepository

    async def register_user(self, credentials: FullCredentials) -> User:
        lg.info("hash password")
        hashed_password = await hash_password(credentials.password)
        new_credentials = HashedCredentials(
            **credentials.model_dump(exclude={"password"}),
            password_hash=hashed_password,
        )

        try:
            lg.info(
                "create user with data",
                extra=new_credentials.model_dump(exclude={"password_hash"}),
            )
            user = await self.UserRepository.create_new_user(new_credentials)
            lg.info("success user create", extra={"id": user.id})
            return user
        except IntegrityError:
            lg.exception("db integrity error")
            raise UserAlreadyExists("User already exists")

    async def authenticate_user(self, credentials: AuthCreds) -> User:
        lg.info(
            "select user with data", extra=credentials.model_dump(exclude={"password"})
        )
        user = await self.UserRepository.select_user(credentials)

        if not user:
            await verify_password(credentials.password, dummy_hash)
            raise UserNotExists("User not Exists")

        elif not await verify_password(credentials.password, user.password_hash):
            raise WrongPassword("Wrong password")

        lg.info("success user select", extra={"id": user.id})
        return user
