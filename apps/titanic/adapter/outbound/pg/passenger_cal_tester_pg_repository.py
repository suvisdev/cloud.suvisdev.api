from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_cal_tester_repository import CalPistolRepository

logger = logging.getLogger(__name__)


class CalPistolPgRepository(CalPistolRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_pistol(self, request: dict[str, Any]) -> None:
        logger.info("[%s] %s request=%s", "CalPistolPgRepository", "get_pistol", request)
        return None
