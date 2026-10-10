from uuid import UUID

from pydantic import TypeAdapter

from .auth import OutputUser
from .base import Base
from .chair import SChairFReservation
from .show import SShowFReservation


class SNewReservation(Base):
    show_id: UUID
    chair_id: UUID


class SReservationOutput(Base):
    id: UUID
    chair_id: UUID
    show: SShowFReservation
    chair: SChairFReservation


class SReservationOutputAdmin(SReservationOutput):
    user: OutputUser


SReservationOutput_adapter = TypeAdapter(list[SReservationOutput])
SReservationOutputAdmin_adapter = TypeAdapter(list[SReservationOutputAdmin])
