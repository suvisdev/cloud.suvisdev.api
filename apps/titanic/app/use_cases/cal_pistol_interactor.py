from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.cal_pistol_use_case import CalPistolUseCase
from titanic.app.ports.output.cal_pistol_repository import CalPistolRepository

logger = logging.getLogger(__name__)


class CalPistolInteractor(CalPistolUseCase):
    """cal_pistol_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: CalPistolRepository | None = None) -> None:
        self._repository = repository

    async def get_pistol(self, request: dict[str, Any]) -> None:
        logger.info("🤖 [CalPistolInteractor] get_pistol 진입")
        await self._repository.get_pistol(request)
        logger.info("🤖 [CalPistolInteractor] get_pistol 완료")
