from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinInteractor(HartleyViolinUseCase):
    """hartley_violin_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: HartleyViolinRepository | None = None) -> None:
        self._repository = repository

    async def get_violin(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [HartleyViolinInteractor] get_violin 진입")
        result = await self._repository.get_violin(request)
        logger.info("🤖 [HartleyViolinInteractor] get_violin 완료")
        return result
