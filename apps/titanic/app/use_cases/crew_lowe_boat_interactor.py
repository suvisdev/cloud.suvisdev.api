from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_repository import LoweBoatRepository

logger = logging.getLogger(__name__)


class LoweBoatInteractor(LoweBoatUseCase):
    def __init__(self, repository: LoweBoatRepository) -> None:
        self._repository = repository

    async def get_boat(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "LoweBoatInteractor", "get_boat")
        return await self._repository.get_boat(request)
