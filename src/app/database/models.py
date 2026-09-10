import uuid
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    declarative_mixin,
    mapped_column,
    relationships,
)


class Roles(StrEnum):
    user = "user"
    admin = "admin"


class Base(MappedAsDataclass, DeclarativeBase):
    __tablename__ = "base"


@declarative_mixin
class IDMixin:
    ID: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        autoincrement=False,
        index=True,
        unique=True,
    )


class User(IDMixin, Base):
    __tablename__ = "users"

    nickname: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(True),
        server_default=func.now(),
    )
    Role: Mapped[Roles] = mapped_column(default=Roles.user)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)


class Movie(IDMixin, Base):
    __tablename__ = "movies"
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    genre: Mapped[str] = mapped_column()
    director: Mapped[str] = mapped_column()


class Show(IDMixin, Base):
    __tablename__ = "shows"
    movie_id: Mapped[UUID] = mapped_column(ForeignKey(Movie.ID))
    start: Mapped[datetime] = mapped_column()
    finish: Mapped[datetime] = mapped_column()


class Hall(IDMixin, Base):
    __tablename__ = "hall"

    chair_number: Mapped[int] = mapped_column()
    show_id: Mapped[UUID] = mapped_column(ForeignKey(Show.ID))
    reservation: Mapped[bool]


class Reservation(IDMixin, Base):
    __tablename__ = "reservations"
    movie_id: Mapped[UUID] = mapped_column(ForeignKey(Movie.ID))
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.ID))
    chair_id: Mapped[UUID] = mapped_column(ForeignKey(Hall.ID))
    start: Mapped[datetime] = mapped_column()
    finish: Mapped[datetime] = mapped_column()
