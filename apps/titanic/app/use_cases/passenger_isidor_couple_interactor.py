from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorBedUseCase
from titanic.app.ports.output.passenger_isidor_couple_repository import IsidorBedRepository

logger = logging.getLogger(__name__)


class IsidorBedInteractor(IsidorBedUseCase):
    def __init__(self, repository: IsidorBedRepository) -> None:
        self._repository = repository

    async def get_bed(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "IsidorBedInteractor", "get_bed")
        return await self._repository.get_bed(request)
