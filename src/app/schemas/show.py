from datetime import datetime
from uuid import UUID

from .base import Base
from .hall import SHallOutput


class SShowOutput(Base):
    hall: SHallOutput
    movie_id: UUID
    start: datetime
    finish: datetime
    hall_id: UUID
