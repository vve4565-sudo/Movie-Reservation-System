from datetime import datetime
from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_show_service
from database.models import User
from fastapi import APIRouter, Depends, status
from service.show import ShowService

router = APIRouter(prefix="/shows", tags=["show"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_id: str,
    start: datetime,
    finish: datetime,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    id = await show_service.create_show(UUID(movie_id), start, finish)
    return id


@router.get("/")
async def get_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    id: str,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    result = await show_service.get_show(UUID(id))
    return result


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    id: str,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    return await show_service.delete_show(UUID(id))

@router.get('/avalabile')
async def get_all_shows(
    show_service: Annotated[ShowService, Depends(get_show_service)],
    start: datetime = datetime.now(),
    finish: datetime | None = None,
):
    return await show_service.get_all_shows(start, finish)
