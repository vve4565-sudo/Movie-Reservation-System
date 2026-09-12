from fastapi import APIRouter

router = APIRouter(prefix="/movies")


@router.get("/")
async def get_allowed_movies(limit: int, cursor: str): ...
