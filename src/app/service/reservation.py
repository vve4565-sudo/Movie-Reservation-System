from dataclasses import dataclass
from uuid import UUID

from exceptions.reservation import ReservationNotExists
from repository.reservation import ReservationRepository


@dataclass
class ReservationService:
    reservation_repository: ReservationRepository

    async def new_reservation(self, show_id: UUID, user_id: UUID, chair_id: UUID):
        return await self.reservation_repository.new_reservation(
            show_id,
            user_id,
            chair_id,
        )

    async def get_all_reservations(self):
        return await self.reservation_repository.get_all_reservations()

    async def get_reservation_by_id(self, show_id: UUID):
        result = await self.reservation_repository.get_reservation_by_id(show_id)
        if result:
            return result

        raise ReservationNotExists("Reservation not exist")

    async def delete_reservation(self, reservation_id: UUID):
        return await self.reservation_repository.delete_reservation(reservation_id)
