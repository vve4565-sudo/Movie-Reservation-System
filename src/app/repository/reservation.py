from dataclasses import dataclass
from uuid import UUID

from database.models import Hall, Movie, Reservation, Show
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ReservationRepository:
    session: AsyncSession

    async def new_reservation(self, show_id: UUID, user_id: UUID, hall_id: UUID):
        new_reservation = Reservation(
            show_id=show_id,
            user_id=user_id,
            hall_id=hall_id,
        )
        self.session.add(new_reservation)
        await self.session.commit()
        return new_reservation.id

    async def get_all_reservations(self):
        query = select(Reservation).join(Hall).join(Movie).join(Show)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_reservation_by_id(self, hall_id: UUID):
        query = (
            select(Reservation)
            .where(Reservation.hall_id == hall_id)
            .join(Hall)
            .join(Movie)
            .join(Show)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_reservation(self, reservation_id: UUID):
        query = delete(Reservation).where(Reservation.id == reservation_id)
        await self.session.execute(query)
        return
