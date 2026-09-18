from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_reservation_service
from database.models import User
from fastapi import APIRouter, Depends, status
from schemas.reservation import SNewReservation
from service.reservation import ReservationService

router = APIRouter(prefix="/reservation", tags=["reservation"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_reservation(
    data: SNewReservation,
    admin: Annotated[User, Depends(current_user_is_admin)],
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    return await reservation_service.new_reservation(**data.model_dump())


@router.get("/")
async def get_reservations(
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    return await reservation_service.get_all_reservations()


@router.get("/{hall_id}")
async def get_reservation_by_id(
    hall_id: UUID,
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    return await reservation_service.get_reservation_by_id(hall_id)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: UUID,
    admin: Annotated[User, Depends(current_user_is_admin)],
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    return await reservation_service.delete_reservation(reservation_id)
