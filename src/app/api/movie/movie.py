from typing import Annotated
from uuid import UUID

from api.Depends import current_user_is_admin, get_movie_service
from database.models import User
from fastapi import APIRouter, Depends, UploadFile, status
from schemas.movie import MovieImage, MovieImagePatch, MoviePatch, NewMovie, OutputMovie
from service.movie import MovieService

router = APIRouter(prefix="/movies")


@router.get("/")
async def get_allowed_movies(
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
    cursor: str | None = None,
    limit: int = 10,
) -> tuple[list[OutputMovie], UUID]:
    result = await movie_service.get_movies(limit, cursor)
    return result  # type: ignore


@router.post("/", status_code=status.HTTP_201_CREATED)
async def new_movie(
    admin: Annotated[User, Depends(current_user_is_admin)],
    data: NewMovie,
    image: UploadFile,
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
):
    movie_image = MovieImage(image=await image.read(), title=image.filename)  # type: ignore
    id = await movie_service.new_movie(data, movie_image)
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

    if not data:
        data = MoviePatch()

    movie_image = MovieImagePatch(image=await image.read(), title=image.filename)  # type: ignore

    id = await movie_service.patch_movie_data(UUID(id), data, movie_image)  # type: ignore
    return id


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    id: str,
    admin: Annotated[User, Depends(current_user_is_admin)],
    movie_service: Annotated[MovieService, Depends(get_movie_service)],
):
    await movie_service.delete_movie(UUID(id))
    return
