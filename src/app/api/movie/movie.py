import logging
from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_movie_service
from database.models import User
from exceptions.movie import (
    ImageSaveError,
    InvalidImageExtensionError,
    MovieImageNotExists,
)
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from schemas.movie import (
    MovieImage,
    MovieImagePatch,
    MoviePatch,
    NewMovie,
    SOutputMovie,
)
from service.movie import MovieService

router = APIRouter(prefix="/movies", tags=["movie"])
lg = logging.getLogger(__name__)


@router.get("/{id}")
async def get_movie_by_id(
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
    id: str,
) -> SOutputMovie:

    lg.info("get movie by id", extra={"id": id})
    result = await movie_service.get_movie(UUID(id))
    lg.info("success movie select")
    return result  # type: ignore


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_movie(
    image: UploadFile,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    genre: Annotated[str, Form()],
    director: Annotated[str, Form()],
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
    length: Annotated[int, Form()],
):
    if image.size > 200:  # type: ignore
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="image size must be less than 200 mb"
        )
    lg.info("serialize file as MovieImage object")
    movie_image = MovieImage(image=await image.read(), title=image.filename)  # type: ignore
    data = NewMovie(
        title=title,
        description=description,
        genre=genre,
        director=director,
        length=length,
    )
    lg.info("create movie with data", extra=data.model_dump())
    try:
        id = await movie_service.new_movie(data, movie_image)

    except ImageSaveError:
        lg.exception("movie image save error", extra={"title": movie_image.title})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except InvalidImageExtensionError:
        lg.exception("invalid image extension")
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    lg.info("success movie create", extra={"id": id})
    return id


@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def patch_movie_data(
    admin: Annotated[User, Depends(current_user_is_admin)],
    id: str,
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
    data: MoviePatch | None = None,
    image: UploadFile | None = None,
):
    if not image:
        movie_image = MovieImagePatch()

    else:
        lg.info("serialize file as image")
        movie_image = MovieImagePatch(image=await image.read(), title=image.filename)  # type: ignore

    if not data:
        data = MoviePatch()

    lg.info("create movie with data", extra=data.model_dump())
    try:
        await movie_service.patch_movie_data(UUID(id), data, movie_image)
    except ImageSaveError:
        lg.exception("movie image save error", extra={"id": id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    lg.info("success movie create", extra={"id": id})
    return id


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    id: str,
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
):
    lg.info("delete movie with id", extra={"id": id})
    await movie_service.delete_movie(UUID(id))
    lg.info("success movie delete", extra={"id": id})
    return


@router.get("/")
async def get_movies(
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
):
    lg.info("select all movies")
    result = await movie_service.get_movies()
    lg.info("success select movies")
    return result


@router.get("/images/{image_path}")
async def get_image(
    image_path: str, movie_service: Annotated[MovieService, Depends(get_movie_service)]
):
    lg.info("get movie image", extra={"path": image_path})
    try:
        result = await movie_service.get_image(image_path)
        lg.info("success get movie image")
        return result
    except MovieImageNotExists as e:
        lg.error(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND)
