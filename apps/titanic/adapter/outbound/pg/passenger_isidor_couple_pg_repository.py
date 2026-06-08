from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_isidor_couple_repository import IsidorBedRepository

logger = logging.getLogger(__name__)


class IsidorBedPgRepository(IsidorBedRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_bed(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "IsidorBedPgRepository", "get_bed", request)
        return 0
