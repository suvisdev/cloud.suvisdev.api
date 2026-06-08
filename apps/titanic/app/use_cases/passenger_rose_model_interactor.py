from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_rose_model_use_case import RoseDiamondUseCase
from titanic.app.ports.output.passenger_rose_model_repository import RoseDiamondRepository

logger = logging.getLogger(__name__)


class RoseDiamondInteractor(RoseDiamondUseCase):
    def __init__(self, repository: RoseDiamondRepository) -> None:
        self._repository = repository

    async def get_diamond(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "RoseDiamondInteractor", "get_diamond")
        return await self._repository.get_diamond(request)
