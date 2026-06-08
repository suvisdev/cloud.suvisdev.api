from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_ruth_survivor_repository import RuthCorsetRepository

logger = logging.getLogger(__name__)


class RuthCorsetPgRepository(RuthCorsetRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_corset(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "RuthCorsetPgRepository", "get_corset", request)
        return 0
