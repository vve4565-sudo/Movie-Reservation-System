import logging
from dataclasses import dataclass
from uuid import UUID

from database.models import Chair, Hall, Show
from sqlalchemy import delete, select
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
