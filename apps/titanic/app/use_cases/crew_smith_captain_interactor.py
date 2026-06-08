from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(self, repository: SmithCaptainRepository) -> None:
        self._repository = repository

    async def get_captain(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "SmithCaptainInteractor", "get_captain")
        return await self._repository.get_captain(request)
