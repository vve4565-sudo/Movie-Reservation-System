from typing import Annotated

from database.database import get_session
from fastapi import Depends
from repository.user import UserRepository
from service.auth import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_auth_repository(session: SessionDep):
    return UserRepository(session)


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_auth_repository)],
):
    return AuthService(user_repository)
