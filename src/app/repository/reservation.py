from dataclasses import dataclass
from uuid import UUID

from database.models import Chair, Movie, Reservation, Show, User
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ReservationRepository:
    session: AsyncSession

    async def new_reservation(self, show_id: UUID, user_id: UUID, chair_id: UUID):
        new_reservation = Reservation(
            show_id=show_id,
            user_id=user_id,
            chair_id=chair_id,
        )
        self.session.add(new_reservation)
        await self.session.commit()
        return new_reservation.id

    async def get_all_reservations(self):
        query = select(Reservation).join(Chair).join(Show).join(User)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_reservation_by_id(self, show_id: UUID):
        query = (
            select(Reservation)
            .where(Reservation.show_id == show_id)
            .join(Chair)
            .join(Show)
            .join(User)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_reservation(self, reservation_id: UUID):
        query = delete(Reservation).where(Reservation.id == reservation_id)
        await self.session.execute(query)
        return
