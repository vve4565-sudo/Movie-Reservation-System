import logging
import os
from dataclasses import dataclass
from uuid import UUID

from aiofiles import open
from config.config import config
from config.redis import movie_cache
from database.models import Movie
from exceptions.movie import (
    ImageSaveError,
    InvalidImageExtensionError,
    MovieImageNotExists,
)
from fastapi.responses import FileResponse
from repository.movie import MovieRepository
from schemas.movie import (
    MovieImage,
    MovieImagePatch,
    MoviePatch,
    NewMovie,
    SOutputMovie,
)

lg = logging.getLogger(__name__)


@dataclass
class MovieService:
    movie_repository: MovieRepository

    async def get_movie(self, id: UUID) -> Movie:

        lg.info("get movie by id", extra={"id": str(id)})
        result = await self.movie_repository.get_movie_by_id(id)
        lg.info("success movie select")

        return result

    async def new_movie(self, data: NewMovie, image: MovieImage) -> UUID:
        lg.info("create movie with data", extra=data.model_dump())

        if image.title.split(".")[-1] not in ["png", "jpeg", "jpg", "ico", "csv"]:
            raise InvalidImageExtensionError()

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

    @movie_cache
    async def get_movies(self):
        lg.info("select all movies")
        result = await self.movie_repository.get_movies()
        serialized_result = [SOutputMovie.model_validate(x) for x in result]
        lg.info("success movies select")
        return serialized_result

    async def get_image(self, image_path: str):
        lg.info("get movie image", extra={"path": image_path})
        if not os.path.exists(f"\\storage\\{image_path}"):
            raise MovieImageNotExists("movie image not exists")

        return FileResponse(f"\\storage\\{image_path}")
