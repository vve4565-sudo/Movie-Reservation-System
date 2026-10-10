import logging
from typing import Annotated
from uuid import UUID

from api.Depends import current_user, current_user_is_admin, get_reservation_service
from database.models import Roles, User
from exceptions.reservation import ReservationAlredyExist
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.reservation import (
    SNewReservation,
    SReservationOutput,
    SReservationOutput_adapter,
    SReservationOutputAdmin,
    SReservationOutputAdmin_adapter,
)
from service.reservation import ReservationService

router = APIRouter(prefix="/reservation", tags=["reservation"])
lg = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_reservation(
    data: SNewReservation,
    user: Annotated[User, Depends(current_user)],
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
):
    lg.info("create new reservation")
    try:
        result = await reservation_service.new_reservation(
            **data.model_dump(), user_id=user.id
        )
    except ReservationAlredyExist:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="reservation already exist"
        )
    lg.info("success create new reservation")
    return result


# @router.get("/")
# async def get_reservations(
#     reservation_service: Annotated[
#         ReservationService, Depends(get_reservation_service)
#     ],
# ) -> list[SReservationOutput]:
#     lg.info("select all reservations")
#     result = await reservation_service.get_all_reservations()
#     lg.info("success select all reservations")
#     return result


@router.get("/")
async def get_reservations(
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
    admin: Annotated[User, Depends(current_user_is_admin)],
) -> list[SReservationOutputAdmin]:
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
) -> list[SReservationOutput]:
    lg.info("select reservation by show id")
    result = await reservation_service.get_reservation_by_show_id(show_id)
    lg.info("success select reservation by id")
    return result


@router.get("/admin/show/{show_id}")
async def get_reservation_by_show_id(
    show_id: UUID,
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
    admin: Annotated[User, Depends(current_user_is_admin)],
) -> list[SReservationOutputAdmin]:
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


@router.get("/user/{user_id}")
async def get_reservation_by_user_id(
    user_id: UUID,
    reservation_service: Annotated[
        ReservationService, Depends(get_reservation_service)
    ],
    user: Annotated[User, Depends(current_user)],
):
    lg.info("select reservation by show id")
    result = await reservation_service.get_reservation_by_user_id(user_id)
    lg.info("success select reservation by id")

    if user.Role == Roles.admin:
        return SReservationOutputAdmin_adapter.validate_python(result)

    return SReservationOutput_adapter.validate_python(result)
