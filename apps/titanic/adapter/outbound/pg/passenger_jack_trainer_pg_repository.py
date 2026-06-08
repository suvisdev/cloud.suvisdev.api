from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_jack_trainer_repository import JackSketchRepository

logger = logging.getLogger(__name__)


class JackSketchPgRepository(JackSketchRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_sketch(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "JackSketchPgRepository", "get_sketch", request)
        return 0
