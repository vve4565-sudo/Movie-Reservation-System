import logging
from dataclasses import dataclass
from uuid import UUID

from database.models import Chair, Hall
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

lg = logging.getLogger(__name__)


@dataclass
class HallRepository:
    session: AsyncSession

    async def get_chairs_by_hall_id(self, hall_id: UUID):
        lg.info("select chairs by hall_id", extra={"hall_id": hall_id})
        query = select(Chair).where(Chair.hall_id == hall_id)
        result = await self.session.execute(query)
        lg.info("success select chairs by id", extra={"hall_id": hall_id})
        return result.scalars().all()

    async def get_available_halls(self):
        lg.info("select available halls")
        query = select(Hall)
        result = await self.session.execute(query)
        lg.info("success select halls")
        return result.scalars().all()

    async def get_hall_by_chair_id(self, chair_id: UUID):
        query = select(Hall).join(Chair).where(Chair.id == chair_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
