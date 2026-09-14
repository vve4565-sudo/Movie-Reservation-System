import logging
from dataclasses import dataclass
from uuid import UUID

from aiofiles import open
from config.config import config
from database.models import Movie
from exceptions.movie import ImageSaveError
from repository.movie import MovieRepository
from schemas.movie import MovieImage, MovieImagePatch, MoviePatch, NewMovie

lg = logging.getLogger(__name__)


@dataclass
class MovieService:
    movie_repository: MovieRepository

    async def get_movies(self, id: UUID) -> Movie:

        lg.info("get movie by id", extra={"id": str(id)})
        result = await self.movie_repository.get_movie_by_id(id)
        lg.info("success movie select")

        return result

    async def new_movie(self, data: NewMovie, image: MovieImage) -> UUID:
        lg.info("create movie with data", extra=data.model_dump())

        try:
            async with open(
                config.BASE_STORAGE_URL + "/" + image.title,
                mode="wb",
            ) as f:
                await f.write(image.image)
            lg.info("image saved", extra={"title": image.title})

        except Exception:
            lg.exception("movie image save error", extra={"title": image.title})
            raise ImageSaveError("Image save error")

        lg.info(
            "create movie with data",
            extra={"data": data.model_dump(), "image_title": image.title},
        )
        id = await self.movie_repository.new_movie(data, image.title)
        lg.info("success movie create", extra={"id": id})
        return id

    async def patch_movie_data(
        self, id: UUID, data: MoviePatch, image: MovieImagePatch
    ) -> UUID:
        lg.info(
            "patch movie with data", extra={"id": str(id), "data": data.model_dump()}
        )

        try:
            if image.title and image.image:
                async with open(config.BASE_STORAGE_URL + image.title, mode="wb") as f:
                    await f.write(image.image)
                lg.info("image patched", extra={"title": image.title})
        except Exception:
            lg.exception("image patch error", extra={"title": image.title})
            raise ImageSaveError("Image save error")

        lg.info(
            "patch movie with data", extra={"id": str(id), "data": data.model_dump()}
        )
        if image.title:
            id = await self.movie_repository.patch_movie_data(id, data, image.title)
            lg.info("success movie patch", extra={"id": id})
            return id
        raise ImageSaveError("Image title not found")

    async def delete_movie(self, id: UUID) -> None:
        lg.info("delete movie with data", extra={"id": str(id)})

        try:
            await self.movie_repository.delete_movie(id)
            lg.info("success movie delete", extra={"id": str(id)})
            return
        except Exception:
            lg.exception("movie delete error", extra={"id": str(id)})
            raise
