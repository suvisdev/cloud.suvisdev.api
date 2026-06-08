from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_cal_tester_use_case import CalPistolUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalPistolRepository

logger = logging.getLogger(__name__)


class CalPistolInteractor(CalPistolUseCase):
    def __init__(self, repository: CalPistolRepository) -> None:
        self._repository = repository

    async def get_pistol(self, request: dict[str, Any]) -> None:
        logger.info("[%s] %s", "CalPistolInteractor", "get_pistol")
        return await self._repository.get_pistol(request)
