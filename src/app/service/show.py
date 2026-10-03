import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from config.redis import show_cache
from database.models import Show
from exceptions.show import ShowsNotExists
from repository.hall import HallRepository
from repository.movie import MovieRepository
from repository.show import ShowRepository
from schemas.show import SShowOutput

lg = logging.getLogger(__name__)


@dataclass
class ShowService:
    show_repository: ShowRepository
    movie_repository: MovieRepository
    hall_repository: HallRepository

    async def create_show(
        self,
        movie_id: UUID,
        start: datetime,
    ) -> UUID:
        lg.info("select movie.lenght from database")
        movie_lenght = (await self.movie_repository.get_movie_by_id(movie_id)).lenght
        finish = start + timedelta(seconds=movie_lenght)
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

    @show_cache
    async def get_all_shows(
        self,
        movie_id: UUID,
        start: datetime,
    ):
        lg.info("get all shows with params", extra={"start": start})
        result = await self.show_repository.get_all_shows(
            movie_id,
            start,
        )
        serialized_result = [
            SShowOutput.model_validate(x, from_attributes=True) for x in result
        ]
        lg.info("success show select")
        return serialized_result

    async def get_chairs_by_hall_id(self, hall_id: UUID):
        lg.info("select hall by hall_id", extra={"hall_id": hall_id})
        result = await self.hall_repository.get_chairs_by_hall_id(hall_id)
        lg.info("success select hall by id", extra={"hall_id": hall_id})
        return result
