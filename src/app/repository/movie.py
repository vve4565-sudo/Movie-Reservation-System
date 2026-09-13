from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from config.config import config
from database.models import Movie
from schemas.movie import MoviePatch, NewMovie
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class MovieRepository:
    session: AsyncSession

    async def get_movies(
        self,
        limit: int,
        cursor: UUID | None,
    ) -> tuple[Sequence[Movie], UUID]:
        if cursor:
            query = select(Movie).where(Movie.id < cursor).limit(limit)
        else:
            query = select(Movie).limit(limit)

        result = await self.session.execute(query)
        res = result.scalars().all()
        return (res, res[-1].id)

    async def new_movie(self, data: NewMovie, image_title: str) -> UUID:
        movie = Movie(**data.model_dump(), image=config.BASE_STORAGE_URL + image_title)
        self.session.add(movie)
        await self.session.commit()
        return movie.id

    async def patch_movie_data(
        self,
        id: UUID,
        data: MoviePatch,
        image_title: str | None = None,
    ) -> UUID:

        if not image_title:
            raise Exception("temporal exc")

        update(Movie).where(Movie.id == id).values(
            data.model_dump(exclude_none=True), image=image_title
        )
        return id

    async def delete_movie(self, id: UUID) -> None:
        delete(Movie).where(Movie.id == id)

        return
