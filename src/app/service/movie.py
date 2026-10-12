import logging
import os
from dataclasses import dataclass
from uuid import UUID, uuid4

from aiofiles import open
from fastapi.responses import FileResponse

from app.config.config import config
from app.config.redis import invalidate_movie_cache, movie_cache
from app.database.models import Movie
from app.exceptions.movie import (
    ImageSaveError,
    InvalidImageExtensionError,
    MovieImageNotExists,
    MovieNotExists,
)
from app.repository.movie import MovieRepository
from app.schemas.movie import (
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

    async def get_movie(self, id: UUID) -> Movie | None:

        lg.info("get movie by id", extra={"id": str(id)})
        result = await self.movie_repository.get_movie_by_id(id)
        lg.info("success movie select")

        return result

    async def new_movie(self, data: NewMovie, image: MovieImage) -> UUID:
        lg.info("create movie with data", extra=data.model_dump())

        if image.title.split(".")[-1] not in ["png", "jpeg", "jpg", "ico"]:
            raise InvalidImageExtensionError()

        new_image_title = str(uuid4())

        try:
            async with open(
                config.BASE_STORAGE_URL / new_image_title,
                mode="wb",
            ) as f:
                await f.write(image.image)
            lg.info("image saved", extra={"title": new_image_title})

        except Exception:
            lg.exception("movie image save error", extra={"title": new_image_title})
            raise ImageSaveError("Image save error")

        lg.info(
            "create movie with data",
            extra={"data": data.model_dump(), "image_title": new_image_title},
        )
        id = await self.movie_repository.new_movie(data, new_image_title)
        lg.info("success movie create", extra={"id": id})
        lg.info("try invalidate cache")
        await invalidate_movie_cache()
        lg.info("success cache invalidate")
        return id

    async def patch_movie_data(
        self,
        id: UUID,
        data: MoviePatch | None,
        image: MovieImagePatch | None,
    ) -> UUID:
        lg.debug("get old movie data")
        old_data = await self.movie_repository.get_movie_by_id(id)
        if not old_data:
            raise MovieNotExists()

        if image:
            lg.info(
                "patch movie image",
                extra={"id": str(id)},
            )
            try:
                if image.image:
                    async with open(
                        config.BASE_STORAGE_URL / old_data.image, mode="wb"
                    ) as f:
                        await f.write(image.image)
                    lg.info("image patched", extra={"image title": old_data.image})
            except Exception:
                lg.exception("image patch error", extra={"image title": old_data.image})
                raise ImageSaveError("Image save error")

        if data:
            lg.info(
                "patch movie with data",
                extra={"id": str(id), "data": data.model_dump()},
            )
            id = await self.movie_repository.patch_movie_data(id, data)
            lg.info("success movie patch", extra={"id": id})
            lg.info("try invalidate cache")
            await invalidate_movie_cache()
            lg.info("success cache invalidate")
            return id

    async def delete_movie(self, id: UUID) -> None:
        lg.info("delete movie with data", extra={"id": str(id)})

        await self.movie_repository.delete_movie(id)
        lg.info("success movie delete", extra={"id": str(id)})
        lg.info("try invalidate cache")
        await invalidate_movie_cache()
        lg.info("success cache invalidate")
        return

    @movie_cache
    async def get_movies(self):
        lg.info("select all movies")
        result = await self.movie_repository.get_movies()
        serialized_result = [SOutputMovie.model_validate(x) for x in result]
        lg.info("success movies select")
        return serialized_result

    async def get_image(self, image_path: str):
        lg.info("get movie image", extra={"path": image_path})
        full_path = config.BASE_STORAGE_URL / image_path
        if not os.path.exists(full_path):
            raise MovieImageNotExists("movie image not exists")

        return FileResponse(full_path)
