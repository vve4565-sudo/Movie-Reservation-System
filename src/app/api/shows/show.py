import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.Depends import current_user_is_admin, get_show_service
from app.database.models import User
from app.exceptions.movie import MovieNotExists
from app.exceptions.show import ShowsNotExists
from app.schemas.chair import SChairOutput
from app.service.show import ShowService

router = APIRouter(prefix="/shows", tags=["show"])
lg = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_id: str,
    hall_id: str,
    start: datetime,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    lg.info(
        "create show with data",
        extra={"movie_id": movie_id, "hall_id": hall_id, "start": start},
    )
    try:
        id = await show_service.create_show(UUID(movie_id), UUID(hall_id), start)
    except MovieNotExists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="movie not exist")
    lg.info("success show create", extra={"id": id})
    return id


@router.get("/")
async def get_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    id: str,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    lg.info("get show with id", extra={"id": id})
    try:
        result = await show_service.get_show(UUID(id))
    except ShowsNotExists:
        lg.exception("show not exists", extra={"id": id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    lg.info("success show select")
    return result


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    id: str,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    lg.info("delete show with id", extra={"id": id})
    result = await show_service.delete_show(UUID(id))
    lg.info("success show delete", extra={"id": id})
    return result


@router.get("/available/")
async def get_all_shows(
    show_service: Annotated[ShowService, Depends(get_show_service)],
    movie_id: UUID,
    start: datetime | None,
):
    if not start:
        start = datetime.now(UTC)
    lg.info("get all shows with params", extra={"start": start})
    result = await show_service.get_all_shows(movie_id=movie_id, start=start)
    lg.info("success show select")
    return result


@router.get("/hall/{hall_id}/")
async def get_chairs_by_hall_id(
    hall_id: str,
    show_service: Annotated[ShowService, Depends(get_show_service)],
) -> list[SChairOutput]:
    lg.info("select hall by hall_id", extra={"hall_id": hall_id})
    result = await show_service.get_chairs_by_hall_id(UUID(hall_id))
    lg.info("success select hall by id", extra={"hall_id": hall_id})
    return result
