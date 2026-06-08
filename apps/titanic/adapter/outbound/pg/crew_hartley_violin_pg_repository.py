from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinPgRepository(HartleyViolinRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_violin(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "HartleyViolinPgRepository", "get_violin", request)
        return 0
