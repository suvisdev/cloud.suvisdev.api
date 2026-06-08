from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsBlueprintRepository

logger = logging.getLogger(__name__)


class AndrewsBlueprintPgRepository(AndrewsBlueprintRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_blueprint(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "AndrewsBlueprintPgRepository", "get_blueprint", request)
        return 0
