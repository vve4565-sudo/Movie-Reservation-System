import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.exceptions.reservation import ChairAndShowNotMatched, ReservationAlredyExist
from app.service.reservation import ReservationService


def make_reservation_service(
    hall_id: UUID | None,
    show_hall_id: UUID | None,
    reservation_result: object = None,
    reservation_error: Exception | None = None,
) -> tuple[ReservationService, AsyncMock]:
    hall_repository = AsyncMock()
    show_repository = AsyncMock()
    reservation_repository = AsyncMock()
    hall_repository.get_hall_by_chair_id.return_value = (
        SimpleNamespace(id=hall_id) if hall_id else None
    )
    show_repository.get_show.return_value = (
        SimpleNamespace(hall_id=show_hall_id) if show_hall_id else None
    )

    if reservation_error:
        reservation_repository.new_reservation.side_effect = reservation_error
    else:
        reservation_repository.new_reservation.return_value = reservation_result

    return (
        ReservationService(
            reservation_repository=reservation_repository,
            hall_repository=hall_repository,
            show_repository=show_repository,
        ),
        reservation_repository,
    )


def test_new_reservation_rejects_chair_from_another_hall() -> None:
    service, reservation_repository = make_reservation_service(
        hall_id=UUID(int=1),
        show_hall_id=UUID(int=2),
    )

    with pytest.raises(ChairAndShowNotMatched):
        asyncio.run(
            service.new_reservation(
                show_id=UUID(int=3),
                user_id=UUID(int=4),
                chair_id=UUID(int=5),
            )
        )

    reservation_repository.new_reservation.assert_not_awaited()


def test_new_reservation_creates_reservation_for_matching_hall() -> None:
    reservation_id = UUID(int=6)
    service, reservation_repository = make_reservation_service(
        hall_id=UUID(int=1),
        show_hall_id=UUID(int=1),
        reservation_result=reservation_id,
    )

    result = asyncio.run(
        service.new_reservation(
            show_id=UUID(int=3),
            user_id=UUID(int=4),
            chair_id=UUID(int=5),
        )
    )

    assert result == reservation_id
    reservation_repository.new_reservation.assert_awaited_once_with(
        UUID(int=3),
        UUID(int=4),
        UUID(int=5),
    )


def test_new_reservation_translates_duplicate_repository_error() -> None:
    service, _ = make_reservation_service(
        hall_id=UUID(int=1),
        show_hall_id=UUID(int=1),
        reservation_error=RuntimeError("duplicate key"),
    )

    with pytest.raises(ReservationAlredyExist):
        asyncio.run(
            service.new_reservation(
                show_id=UUID(int=3),
                user_id=UUID(int=4),
                chair_id=UUID(int=5),
            )
        )
