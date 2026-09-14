from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from database.models import Show
from exceptions.show import ShowsNotExists
from repository.show import ShowRepository


@dataclass
class ShowService:
    show_repository: ShowRepository

    async def create_show(
        self,
        movie_id: UUID,
        start: datetime,
        finish: datetime,
    ) -> UUID:
        id = await self.show_repository.create_show(movie_id, start, finish)
        return id

    async def get_show(self, id: UUID):

        show = await self.show_repository.get_show(id)
        if not show:
            raise ShowsNotExists("show not exists")

        return show

    async def delete_show(self, id: UUID):
        return await self.show_repository.delete_show(id)

    async def get_all_shows(
        self,
        start: datetime,
        finish: datetime | None = None,
    ) -> Sequence[Show]:
        result = await self.show_repository.get_all_shows(start, finish)
        return result
