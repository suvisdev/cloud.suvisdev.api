from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.output.smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    """smith_captain_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: SmithCaptainRepository | None = None) -> None:
        self._repository = repository

    async def get_captain(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [SmithCaptainInteractor] get_captain 진입")
        result = await self._repository.get_captain(request)
        logger.info("🤖 [SmithCaptainInteractor] get_captain 완료")
        return result
