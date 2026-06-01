from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.ruth_corset_use_case import RuthCorsetUseCase
from titanic.app.ports.output.ruth_corset_repository import RuthCorsetRepository

logger = logging.getLogger(__name__)


class RuthCorsetInteractor(RuthCorsetUseCase):
    """ruth_corset_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: RuthCorsetRepository | None = None) -> None:
        self._repository = repository

    async def get_corset(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [RuthCorsetInteractor] get_corset 진입")
        result = await self._repository.get_corset(request)
        logger.info("🤖 [RuthCorsetInteractor] get_corset 완료")
        return result
