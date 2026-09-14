from typing import Annotated
from uuid import UUID

from config.security import decode_token
from database.database import get_session
from database.models import Roles, User
from fastapi import Depends, HTTPException, Request, status
from repository.movie import MovieRepository
from repository.show import ShowRepository
from repository.user import UserRepository
from service.auth import AuthService
from service.movie import MovieService
from service.show import ShowService
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def current_user(session: SessionDep, request: Request):
    id = request.headers.get("Authorization")
    if id:
        token = id.replace("Bearer", "").strip()

        decoded_token = await decode_token(token)
        uuid = UUID(decoded_token.get("sub"))

        user = await session.get(User, uuid)
        return user
    raise HTTPException(status.HTTP_403_FORBIDDEN)


async def current_user_is_admin(user: Annotated[User, Depends(current_user)]):
    if user.Role == Roles.admin:
        return user

    raise HTTPException(status.HTTP_403_FORBIDDEN)


async def get_auth_repository(session: SessionDep):
    return UserRepository(session)


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_auth_repository)],
):
    return AuthService(user_repository)


async def get_movie_repository(session: SessionDep):
    return MovieRepository(session)


async def get_movie_service(
    movie_repository: Annotated[MovieRepository, Depends(get_movie_repository)],
):
    return MovieService(movie_repository)


async def get_show_repository(session: SessionDep):
    return ShowRepository(session)


async def get_show_service(
    show_repository: Annotated[ShowRepository, Depends(get_show_repository)],
):
    return ShowService(show_repository)
