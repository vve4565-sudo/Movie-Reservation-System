from uuid import UUID

from .base import Base


class SNewReservation(Base):
    show_id: UUID
    user_id: UUID
    chair_id: UUID


class SReservationOutput(Base):
    id: UUID
    show_id: UUID
    user_id: UUID
    chair_id: UUID
