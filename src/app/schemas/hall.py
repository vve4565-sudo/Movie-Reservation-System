from uuid import UUID

from .base import Base


class SHallOutput(Base):
    id: UUID
    hall_number: int
