import logging
from dataclasses import dataclass
from uuid import UUID

from config.config import config
from database.models import Movie
from schemas.movie import MoviePatch, NewMovie
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

lg = logging.getLogger(__name__)


@dataclass
class MovieRepository:
    session: AsyncSession

    async def get_movie_by_id(self, id: UUID) -> Movie:

        lg.info("get movie by id", extra={"id": str(id)})

        query = select(Movie).where(Movie.id == id)

        result = await self.session.execute(query)
        res = result.scalar_one()
        lg.info("success movie select")
        return res

    async def new_movie(self, data: NewMovie, image_title: str) -> UUID:
        lg.info("create movie with data", extra=data.model_dump())
        movie = Movie(**data.model_dump(), image=config.BASE_STORAGE_URL + image_title)
        self.session.add(movie)
        await self.session.commit()
        lg.info("success movie create", extra={"id": movie.id})
        return movie.id

    async def patch_movie_data(
        self,
        id: UUID,
        data: MoviePatch,
        image_title: str,
    ) -> UUID:
        lg.info(
            "patch movie with data", extra={"id": str(id), "data": data.model_dump()}
        )

        update(Movie).where(Movie.id == id).values(
            data.model_dump(exclude_none=True), image=image_title
        )

        await self.session.commit()
        lg.info("success movie patch", extra={"id": id})
        return id

    async def delete_movie(self, id: UUID) -> None:
        lg.info("delete movie with id", extra={"id": id})
        delete(Movie).where(Movie.id == id)
        await self.session.commit()
        lg.info("success movie delete", extra={"id": id})
        return
