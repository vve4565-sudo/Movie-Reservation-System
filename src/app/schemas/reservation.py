from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SNewReservation(BaseModel):
    show_id: UUID
    user_id: UUID
    hall_id: UUID
