from datetime import datetime
from uuid import UUID

from .base import Base
from .hall import SHallOutput
from .movie import SMovieFReservation


class SShowOutput(Base):
    id: UUID
    hall: SHallOutput
    movie_id: UUID
    start: datetime
    finish: datetime
    hall_id: UUID


class SShowFReservation(Base):
    id: UUID
    start: datetime
    finish: datetime
    hall: SHallOutput
    movie: SMovieFReservation
