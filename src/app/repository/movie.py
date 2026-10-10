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

    async def get_movie_by_id(self, id: UUID) -> Movie | None:

        lg.info("get movie by id", extra={"id": str(id)})

        query = select(Movie).where(Movie.id == id)

        result = await self.session.execute(query)
        res = result.scalar_one_or_none()
        lg.info("success movie select")
        return res

    async def new_movie(self, data: NewMovie, image_title: str) -> UUID:
        lg.info("create movie with data", extra=data.model_dump())
        movie = Movie(**data.model_dump(), image=image_title)
        self.session.add(movie)
        await self.session.commit()
        lg.info("success movie create", extra={"id": movie.id})
        return movie.id

    async def patch_movie_data(
        self,
        id: UUID,
        data: MoviePatch,
    ) -> UUID:
        lg.info(
            "patch movie with data", extra={"id": str(id), "data": data.model_dump()}
        )

        statement = (
            update(Movie)
            .where(Movie.id == id)
            .values(data.model_dump(exclude_none=True))
        )
        await self.session.execute(statement)
        await self.session.commit()
        lg.info("success movie patch", extra={"id": id})
        return id

    async def delete_movie(self, id: UUID) -> None:
        lg.info("delete movie with id", extra={"id": id})
        statement = delete(Movie).where(Movie.id == id)
        await self.session.execute(statement)
        await self.session.commit()
        lg.info("success movie delete", extra={"id": id})
        return

    async def get_movies(self):
        lg.info("select all movies")
        query = select(Movie)
        result = await self.session.execute(query)
        lg.info("success select movies")
        return result.scalars().all()
