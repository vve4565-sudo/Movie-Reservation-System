import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from database.models import Movie, Show
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        finish: datetime | None = None,
    ) -> list[Show]:
        lg.info("get all shows with params", extra={"start": start, "finish": finish})
        query = select(Show).where(Show.movie_id == movie_id).where(Show.start <= start)
        if finish:
            query = query.where(Show.finish <= finish)

        query = query.join(Movie)
        result = await self.session.execute(query)
        lg.info("success show select")
        return list(result.scalars().all())
