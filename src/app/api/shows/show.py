import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_show_service
from database.models import User
from exceptions.show import ShowsNotExists
from fastapi import APIRouter, Depends, HTTPException, status
from service.show import ShowService

router = APIRouter(prefix="/shows", tags=["show"])
lg = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_show(
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_id: str,
    start: datetime,
    finish: datetime,
    show_service: Annotated[ShowService, Depends(get_show_service)],
):
    lg.info(
        "create show with data",
        extra={"movie_id": movie_id, "start": start, "finish": finish},
    )

    id = await show_service.create_show(UUID(movie_id), start, finish)
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


@router.get("/available")
async def get_all_shows(
    show_service: Annotated[ShowService, Depends(get_show_service)],
    movie_id: UUID,
    start: datetime = datetime.now(UTC),
    finish: datetime | None = None,
):
    lg.info("get all shows with params", extra={"start": start, "finish": finish})
    result = await show_service.get_all_shows(
        movie_id=movie_id, start=start, finish=finish
    )
    lg.info("success show select")
    return result
