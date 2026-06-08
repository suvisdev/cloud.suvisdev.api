from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_jack_trainer_use_case import JackSketchUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackSketchRepository

logger = logging.getLogger(__name__)


class JackSketchInteractor(JackSketchUseCase):
    def __init__(self, repository: JackSketchRepository) -> None:
        self._repository = repository

    async def get_sketch(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "JackSketchInteractor", "get_sketch")
        return await self._repository.get_sketch(request)
