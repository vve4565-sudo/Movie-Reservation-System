from uuid import UUID

from .base import Base


class SOutputMovie(Base):
    id: UUID
    title: str
    description: str
    genre: str
    director: str
    image: str


class NewMovie(Base):
    title: str
    description: str
    genre: str
    director: str
    length: int


class MovieImage(Base):
    image: bytes
    title: str


class MoviePatch(Base):
    title: str | None = None
    description: str | None = None
    genre: str | None = None
    director: str | None = None
    length: int | None = None


class MovieImagePatch(Base):
    image: bytes | None = None
    title: str | None = None


class SMovieFReservation(Base):
    title: str
