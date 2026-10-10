import asyncio
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models import Movie


def seed_movie(
    session_factory: async_sessionmaker[AsyncSession],
) -> UUID:
    async def insert_movie() -> UUID:
        async with session_factory() as session:
            movie = Movie(
                title="Arrival",
                description="A linguist studies an alien arrival.",
                image="arrival.jpg",
                genre="Drama",
                director="Denis Villeneuve",
                length=116,
            )
            session.add(movie)
            await session.commit()
            return movie.id

    return asyncio.run(insert_movie())


def test_list_movies_uses_test_database(
    client: TestClient,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    movie_id = seed_movie(test_session_factory)

    response = client.get("/movies/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(movie_id),
            "title": "Arrival",
            "description": "A linguist studies an alien arrival.",
            "genre": "Drama",
            "director": "Denis Villeneuve",
            "image": "arrival.jpg",
        }
    ]


def test_get_movie_by_id_uses_test_database(
    client: TestClient,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    movie_id = seed_movie(test_session_factory)

    response = client.get(f"/movies/{movie_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(movie_id)
    assert response.json()["title"] == "Arrival"


def test_admin_reservations_require_authentication(client: TestClient) -> None:
    response = client.get("/reservation/")

    assert response.status_code == 403
