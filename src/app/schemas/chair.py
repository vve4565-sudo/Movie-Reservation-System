from uuid import UUID

from .base import Base


class SChairOutput(Base):
    hall_id: UUID
    chair_number: int
    id: UUID


class SChairFReservation(Base):
    chair_number: int
