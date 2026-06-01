from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.jack_sketch_use_case import JackSketchUseCase
from titanic.app.ports.output.jack_sketch_repository import JackSketchRepository

logger = logging.getLogger(__name__)


class JackSketchInteractor(JackSketchUseCase):
    """jack_sketch_router → 입력 포트 → 출력 포트(repository)."""

    def __init__(self, repository: JackSketchRepository | None = None) -> None:
        self._repository = repository

    async def get_sketch(self, request: dict[str, Any]) -> int:
        logger.info("🤖 [JackSketchInteractor] get_sketch 진입")
        result = await self._repository.get_sketch(request)
        logger.info("🤖 [JackSketchInteractor] get_sketch 완료")
        return result
