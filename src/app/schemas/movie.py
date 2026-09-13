from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OutputMovie(BaseModel):
    id: UUID
    title: str
    description: str
    genre: str
    director: str

    model_config = ConfigDict(from_attributes=True)


class NewMovie(BaseModel):
    title: str
    description: str
    genre: str
    director: str


class MovieImage(BaseModel):
    image: bytes
    title: str


class MoviePatch(BaseModel):
    title: str | None = None
    description: str | None = None
    genre: str | None = None
    director: str | None = None


class MovieImagePatch(BaseModel):
    image: bytes | None = None
    title: str | None = None
