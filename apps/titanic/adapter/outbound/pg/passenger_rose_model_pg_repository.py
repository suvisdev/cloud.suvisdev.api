from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_rose_model_repository import RoseDiamondRepository

logger = logging.getLogger(__name__)


class RoseDiamondPgRepository(RoseDiamondRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_diamond(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "RoseDiamondPgRepository", "get_diamond", request)
        return 0
