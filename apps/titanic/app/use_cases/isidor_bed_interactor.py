from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.isidor_bed_use_case import IsidorBedUseCase
from titanic.app.ports.output.isidor_bed_repository import IsidorBedRepository

logger = logging.getLogger(__name__)


class IsidorBedInteractor(IsidorBedUseCase):
    """isidor_bed_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: IsidorBedRepository | None = None) -> None:
        self._repository = repository

    async def get_bed(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [IsidorBedInteractor] get_bed 진입")
        result = await self._repository.get_bed(request)
        logger.info("🤖 [IsidorBedInteractor] get_bed 완료")
        return result
