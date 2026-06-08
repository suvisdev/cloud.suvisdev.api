from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainPgRepository(SmithCaptainRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_captain(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "SmithCaptainPgRepository", "get_captain", request)
        return 0
