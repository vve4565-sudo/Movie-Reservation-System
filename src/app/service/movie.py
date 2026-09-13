from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiofiles import open
from config.config import config
from repository.movie import MovieRepository
from schemas.movie import MovieImage, MovieImagePatch, MoviePatch, NewMovie


@dataclass
class MovieService:
    movie_repository: MovieRepository

    async def get_movies(
        self, limit: int, cursor: str | None
    ) -> tuple[Sequence[Any], bytes]:
        decoded_cursor = None

        if cursor:
            decoded_cursor = UUID(bytes=urlsafe_b64decode(cursor))

        result, new_cursor = await self.movie_repository.get_movies(
            limit, decoded_cursor
        )
        encoded_cursor = urlsafe_b64encode(str(new_cursor).encode())
        return result, encoded_cursor

    async def new_movie(self, data: NewMovie, image: MovieImage) -> UUID:

        async with open(config.BASE_STORAGE_URL + image.title, mode="wb") as f:
            await f.write(image.image)

        id = await self.movie_repository.new_movie(data, image.title)
        return id

    async def patch_movie_data(self, id: UUID, data: MoviePatch, image: MovieImagePatch) -> UUID:
        if image.title and image.image:
            async with open(config.BASE_STORAGE_URL + image.title, mode="wb") as f:
                await f.write(image.image)

        id = await self.movie_repository.patch_movie_data(id, data, image.title)
        return id

    async def delete_movie(self, id: UUID) -> None:
        await self.movie_repository.delete_movie(id)
        return
