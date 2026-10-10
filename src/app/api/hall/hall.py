import logging
from typing import Annotated

from api.Depends import get_hall_service
from fastapi import APIRouter, Depends
from schemas.hall import SHallOutput
from service.hall import HallService

lg = logging.getLogger(__name__)

router = APIRouter(prefix="/hall", tags=["hall"])


@router.get("/")
async def get_available_halls(
    hall_service: Annotated[HallService, Depends(get_hall_service)],
) -> list[SHallOutput]:
    lg.info("select available halls")
    result = await hall_service.get_available_halls()
    lg.info("success select halls")
    return result
