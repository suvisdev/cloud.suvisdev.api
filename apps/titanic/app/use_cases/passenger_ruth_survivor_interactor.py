from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthCorsetUseCase
from titanic.app.ports.output.passenger_ruth_survivor_repository import RuthCorsetRepository

logger = logging.getLogger(__name__)


class RuthCorsetInteractor(RuthCorsetUseCase):
    def __init__(self, repository: RuthCorsetRepository) -> None:
        self._repository = repository

    async def get_corset(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "RuthCorsetInteractor", "get_corset")
        return await self._repository.get_corset(request)
