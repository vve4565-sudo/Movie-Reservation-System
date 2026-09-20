import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from config.redis import cache_decorator
from database.models import Show
from exceptions.show import ShowsNotExists
from repository.show import ShowRepository

lg = logging.getLogger(__name__)


@dataclass
class ShowService:
    show_repository: ShowRepository

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
        id = await self.show_repository.create_show(movie_id, start, finish)
        lg.info("success show create", extra={"id": id})
        return id

    async def get_show(self, id: UUID):
        lg.info("get show with id", extra={"id": id})
        show = await self.show_repository.get_show(id)
        if not show:
            raise ShowsNotExists("show not exists")
        lg.info("success show select")
        return show

    async def delete_show(self, id: UUID):
        lg.info("delete show with id", extra={"id": id})
        result = await self.show_repository.delete_show(id)
        lg.info("success show delete", extra={"id": id})
        return result

    @cache_decorator(module="shows")
    async def get_all_shows(
        self,
        start: datetime,
        finish: datetime | None = None,
    ) -> Sequence[Show]:
        lg.info("get all shows with params", extra={"start": start, "finish": finish})
        result = await self.show_repository.get_all_shows(start, finish)
        lg.info("success show select")
        return result
