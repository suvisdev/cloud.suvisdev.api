from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.rose_diamond_use_case import RoseDiamondUseCase
from titanic.app.ports.output.rose_diamond_repository import RoseDiamondRepository

logger = logging.getLogger(__name__)


class RoseDiamondInteractor(RoseDiamondUseCase):
    """rose_diamond_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: RoseDiamondRepository | None = None) -> None:
        self._repository = repository

    async def get_diamond(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [RoseDiamondInteractor] get_diamond 진입")
        result = await self._repository.get_diamond(request)
        logger.info("🤖 [RoseDiamondInteractor] get_diamond 완료")
        return result
