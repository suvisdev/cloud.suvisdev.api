from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinInteractor(HartleyViolinUseCase):
    def __init__(self, repository: HartleyViolinRepository) -> None:
        self._repository = repository

    async def get_violin(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "HartleyViolinInteractor", "get_violin")
        return await self._repository.get_violin(request)
