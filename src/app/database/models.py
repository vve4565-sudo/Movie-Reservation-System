from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid7

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_mixin,
    mapped_column,
    relationships,
)


class Roles(StrEnum):
    user = "user"
    admin = "admin"


class Base(DeclarativeBase): ...


@declarative_mixin
class IDMixin:
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7,
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

    movie_id: Mapped[UUID] = mapped_column(ForeignKey(Movie.id))
    start: Mapped[datetime] = mapped_column()
    finish: Mapped[datetime] = mapped_column()


class Hall(IDMixin, Base):
    __tablename__ = "halls"

    hall_number: Mapped[int]


class Chair(IDMixin, Base):
    __tablename__ = "chairs"

    hall_id: Mapped[UUID] = mapped_column(ForeignKey(Hall.id))
    chair_number: Mapped[int]


class Reservation(IDMixin, Base):
    __tablename__ = "reservations"

    show_id: Mapped[UUID] = mapped_column(ForeignKey(Show.id))
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id))
    chair_id: Mapped[UUID] = mapped_column(ForeignKey(Chair.id))
