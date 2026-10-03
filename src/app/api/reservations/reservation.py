import logging
from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_reservation_service
from database.models import User
from fastapi import APIRouter, Depends, status
from schemas.reservation import SNewReservation
from service.reservation import ReservationService

router = APIRouter(prefix="/reservation", tags=["reservation"])
lg = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_reservation(
    data: SNewReservation,
    admin: Annotated[User, Depends(current_user_is_admin)],
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    lg.info("create new reservation")
    result = await reservation_service.new_reservation(**data.model_dump())
    lg.info("success create new reservation")
    return result


@router.get("/")
async def get_reservations(
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    lg.info("select all reservations")
    result = await reservation_service.get_all_reservations()
    lg.info("success select all reservations")
    return result


@router.get("/{show_id}")
async def get_reservation_by_show_id(
    show_id: UUID,
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    lg.info("select reservation by show id")
    result = await reservation_service.get_reservation_by_show_id(show_id)
    lg.info("success select reservation by id")
    return result


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: UUID,
    admin: Annotated[User, Depends(current_user_is_admin)],
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    lg.info("delete reservation")
    result = await reservation_service.delete_reservation(reservation_id)
    lg.info("success delete reservation")
    return result
