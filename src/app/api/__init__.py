from fastapi import APIRouter

from .auth import AuthRouter
from .hall import HallRouter
from .movie import MovieRouter
from .reservations import ReservationRouter
from .shows import ShowRouter

router = APIRouter(prefix="/api", tags=["v1"])
router.include_router(AuthRouter)
router.include_router(HallRouter)
router.include_router(MovieRouter)
router.include_router(ReservationRouter)
router.include_router(ShowRouter)
