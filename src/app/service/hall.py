import logging
from dataclasses import dataclass

from app.repository.hall import HallRepository

lg = logging.getLogger(__name__)


@dataclass
class HallService:
    hall_repository: HallRepository

    async def get_available_halls(self):
        lg.info("select available halls")
        result = await self.hall_repository.get_available_halls()
        lg.info("success select halls")
        return result
