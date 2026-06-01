from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.andrews_blueprint_use_case import AndrewsBlueprintUseCase
from titanic.app.ports.output.andrews_blueprint_repository import AndrewsBlueprintRepository

logger = logging.getLogger(__name__)


class AndrewsBlueprintInteractor(AndrewsBlueprintUseCase):
    """andrews_blueprint_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: AndrewsBlueprintRepository | None = None) -> None:
        self._repository = repository

    async def get_blueprint(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [AndrewsBlueprintInteractor] get_blueprint 진입")
        result = await self._repository.get_blueprint(request)
        logger.info("🤖 [AndrewsBlueprintInteractor] get_blueprint 완료 — result=%s", result)
        return result
