from typing import Annotated
from uuid import UUID

from config.security import decode_token
from database.database import get_session
from database.models import Roles, User
from fastapi import Depends, HTTPException, Request, status
from jwt import ExpiredSignatureError
from repository.hall import HallRepository
from repository.movie import MovieRepository
from repository.reservation import ReservationRepository
from repository.show import ShowRepository
from repository.user import UserRepository
from service.auth import AuthService
from service.hall import HallService
from service.movie import MovieService
from service.reservation import ReservationService
from service.show import ShowService
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def current_user(session: SessionDep, request: Request):
    id = request.headers.get("Authorization")
    if id:
        token = id.replace("Bearer", "").strip()
        try:
            decoded_token = await decode_token(token)
        except ExpiredSignatureError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Token expired")
        except:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, detail="server error"
            )
        if not decoded_token.get("header").get("access"):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="invalid access token"
            )
        uuid = UUID(decoded_token.get("payload").get("sub"))

        user = await session.get(User, uuid)
        if not user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="user not exists")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="user inactive")
        return user
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="non authorized")


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


async def get_hall_repository(session: SessionDep):
    return HallRepository(session)


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
    movie_repository: Annotated[MovieRepository, Depends(get_movie_repository)],
    hall_repository: Annotated[HallRepository, Depends(get_hall_repository)],
):
    return ShowService(show_repository, movie_repository, hall_repository)


async def get_reservation_repository(session: SessionDep):
    return ReservationRepository(session)


async def get_reservation_service(
    reservation_repository: Annotated[
        ReservationRepository, Depends(get_reservation_repository)
    ],
    show_repository: Annotated[ShowRepository, Depends(get_show_repository)],
    hall_repository: Annotated[HallRepository, Depends(get_hall_repository)],
):
    return ReservationService(reservation_repository, hall_repository, show_repository)


async def get_hall_service(
    hall_repository: Annotated[HallRepository, Depends(get_hall_repository)],
):
    return HallService(hall_repository)
