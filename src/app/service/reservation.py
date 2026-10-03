import logging
from dataclasses import dataclass
from uuid import UUID

from exceptions.reservation import ReservationNotExists
from repository.reservation import ReservationRepository

lg = logging.getLogger(__name__)


@dataclass
class ReservationService:
    reservation_repository: ReservationRepository

    async def new_reservation(self, show_id: UUID, user_id: UUID, chair_id: UUID):
        lg.info("create new reservation")
        result = await self.reservation_repository.new_reservation(
            show_id,
            user_id,
            chair_id,
        )
        lg.info("success create new reservation")
        return result

    async def get_all_reservations(self):
        lg.info("select all reservations")
        result = await self.reservation_repository.get_all_reservations()
        lg.info("success select all reservations")
        return result

    async def get_reservation_by_show_id(self, show_id: UUID):
        lg.info("select reservation by show id")
        result = await self.reservation_repository.get_reservation_by_show_id(show_id)
        if result:
            lg.info("success select reservation by id")
            return result

        raise ReservationNotExists("Reservation not exist")

    async def delete_reservation(self, reservation_id: UUID):
        lg.info("delete reservation")
        result = await self.reservation_repository.delete_reservation(reservation_id)
        lg.info("success delete reservation")
        return result
