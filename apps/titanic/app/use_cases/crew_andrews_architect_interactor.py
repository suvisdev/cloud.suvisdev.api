from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsBlueprintUseCase
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsBlueprintRepository

logger = logging.getLogger(__name__)


class AndrewsBlueprintInteractor(AndrewsBlueprintUseCase):
    def __init__(self, repository: AndrewsBlueprintRepository) -> None:
        self._repository = repository

    async def get_blueprint(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "AndrewsBlueprintInteractor", "get_blueprint")
        return await self._repository.get_blueprint(request)
