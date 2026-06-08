from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.crew_lowe_boat_repository import LoweBoatRepository

logger = logging.getLogger(__name__)


class LoweBoatPgRepository(LoweBoatRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_boat(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "LoweBoatPgRepository", "get_boat", request)
        return 0
