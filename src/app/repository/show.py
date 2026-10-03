import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import UUID

from database.models import Hall, Movie, Show
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

lg = logging.getLogger(__name__)


@dataclass
class ShowRepository:
    session: AsyncSession

    async def create_show(
        self,
        movie_id: UUID,
        start: datetime,
        finish: datetime,
    ) -> UUID:
        lg.info(
            "create show with data",
            extra={"movie_id": movie_id, "start": start, "finish": finish},
        )
        show = Show(movie_id=movie_id, start=start, finish=finish)
        self.session.add(show)
        await self.session.commit()
        lg.info("success show create", extra={"id": show.id})
        return show.id

    async def get_show(self, id: UUID) -> Show | None:
        lg.info("get show with id", extra={"id": id})
        query = select(Show).where(Show.id == id)
        result = await self.session.execute(query)
        lg.info("success show select")
        return result.scalar_one_or_none()

    async def delete_show(self, id: UUID) -> None:
        lg.info("delete show with id", extra={"id": id})
        query = delete(Show).where(Show.id == id)
        await self.session.execute(query)
        lg.info("success show delete", extra={"id": id})
        return

    async def get_all_shows(
        self,
        movie_id: UUID,
        start: datetime,
    ) -> list[Show]:
        lg.info("get all shows with params", extra={"start": start})
        query = (
            select(Show, Hall.hall_number)
            .where(Show.movie_id == movie_id, Show.start >= start)
            .options(joinedload(Show.hall))
            .order_by(Show.start.asc())
        )
        result = await self.session.execute(query)
        lg.info("success show select")
        return list(result.scalars().unique().all())
