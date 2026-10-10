import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from database.models import Reservation, Show
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

lg = logging.getLogger(__name__)


@dataclass
class ReservationRepository:
    session: AsyncSession

    async def new_reservation(self, show_id: UUID, user_id: UUID, chair_id: UUID):
        lg.info("create new reservation")
        new_reservation = Reservation(
            show_id=show_id,
            user_id=user_id,
            chair_id=chair_id,
        )
        self.session.add(new_reservation)
        await self.session.commit()
        lg.info("success create new reservation")
        return new_reservation.id

    async def get_all_reservations(self, start: datetime):
        lg.info("select all reservations")
        query = (
            select(Reservation)
            .join(Reservation.show)
            .options(
                joinedload(Reservation.chair),
                joinedload(Reservation.show).joinedload(Show.movie),
                joinedload(Reservation.show).joinedload(Show.hall),
                joinedload(Reservation.user),
            )
            .where(Show.finish > start)
        )
        result = await self.session.execute(query)
        lg.info("success select all reservations")
        return result.scalars().all()

    async def get_reservation_by_show_id(self, show_id: UUID):
        lg.info("select reservation by show_id")
        query = (
            select(Reservation)

            .options(
                joinedload(Reservation.chair),
                joinedload(Reservation.show).joinedload(Show.movie),
                joinedload(Reservation.show).joinedload(Show.hall),
                joinedload(Reservation.user),
            )
            .where(Reservation.show_id == show_id)
        )
        result = await self.session.execute(query)
        lg.info("success select reservation by show_id")
        return result.scalars().all()

    async def delete_reservation(self, reservation_id: UUID):
        lg.info("delete reservation")
        query = delete(Reservation).where(Reservation.id == reservation_id)
        await self.session.execute(query)
        await self.session.commit()
        lg.info("success delete reservation")
        return

    async def get_reservation_by_user_id(self, user_id: UUID):
        lg.info("select reservation by user_id")
        query = (
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .options(
                joinedload(Reservation.chair),
                joinedload(Reservation.show).joinedload(Show.movie),
                joinedload(Reservation.show).joinedload(Show.hall),
                joinedload(Reservation.user),
            )
        )
        result = await self.session.execute(query)
        lg.info("success select reservation by user_id")
        return result.scalars().all()
