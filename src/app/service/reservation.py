from datetime import UTC, datetime
import logging
from dataclasses import dataclass
from uuid import UUID

from exceptions.reservation import ChairAndShowNotMatched, ReservationAlredyExist
from repository.hall import HallRepository
from repository.reservation import ReservationRepository
from repository.show import ShowRepository

lg = logging.getLogger(__name__)


@dataclass
class ReservationService:
    reservation_repository: ReservationRepository
    hall_repository: HallRepository
    show_repository: ShowRepository

    async def new_reservation(self, show_id: UUID, user_id: UUID, chair_id: UUID):
        lg.info("check truth hall_id")
        hall_by_chair = await self.hall_repository.get_hall_by_chair_id(chair_id)
        _show = await self.show_repository.get_show(show_id)
        if not hall_by_chair or not _show or _show.hall_id != hall_by_chair.id:
            raise ChairAndShowNotMatched()

        lg.info("create new reservation")
        try:
            result = await self.reservation_repository.new_reservation(
                show_id,
                user_id,
                chair_id,
            )
        except:
            lg.error("bad create reservation")
            raise ReservationAlredyExist()
        lg.info("success create new reservation")
        return result

    async def get_all_reservations(self):
        lg.info("select all reservations")
        start = datetime.now(UTC)
        result = await self.reservation_repository.get_all_reservations(start)
        lg.info("success select all reservations")
        return result

    async def get_reservation_by_show_id(self, show_id: UUID):
        lg.info("select reservation by show id")
        result = await self.reservation_repository.get_reservation_by_show_id(show_id)
        lg.info("success select reservation by id")
        return result

    async def delete_reservation(self, reservation_id: UUID):
        lg.info("delete reservation")
        result = await self.reservation_repository.delete_reservation(reservation_id)
        lg.info("success delete reservation")
        return result

    async def get_reservation_by_user_id(self, user_id: UUID):
        lg.info("select reservation by show id")
        result = await self.reservation_repository.get_reservation_by_user_id(user_id)
        lg.info("success select reservation by id")
        return result
